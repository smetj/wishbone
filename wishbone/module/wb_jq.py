#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  jq.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from wishbone import Actor
from jq import jq
from jsonschema import validate

import os
import yaml
import gevent_inotifyx as inotify
from gevent.lock import Semaphore
from gevent import sleep
from glob import glob
from yaml.parser import ParserError


SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "expression": {
            "type": "string"
        },
        "queue": {
            "type": "string"
        },
        "payload": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": [
                        "string",
                        "number"
                    ],
                }
            }
        },
    },
    "required": ["name", "expression", "queue"],
    "additionalProperties": False
}

SCHEMA_DISK = {
    "type": "object",
    "properties": {
        "expression": {
            "type": "string"
        },
        "queue": {
            "type": "string"
        },
        "payload": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": [
                        "string",
                        "number"
                    ],
                }
            }
        },
    },
    "required": ["expression", "queue"],
    "additionalProperties": False
}

class JQ(Actor):

    '''**Evaluates a data structure against jq expressions.**

    Evalutes (JSON) data structures against a set of jq expressions to decide
    which queue to forward the event to.

    JQ expressions
    --------------

    More information about jq expressions can be found here:

        - https://stedolan.github.io/jq/manual/


    Jq expressions need to return either **True** or **False**, otherwise this
    module will consider the result to be invalid and therefor skip the
    condition.

    Module level conditions
    -----------------------

    The module accepts the <conditions> parameter which is a list of
    conditions to evaluate against each data structure coming in.
    Each condition should have following format:

    JSON-schema::

        {
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "expression": {
                "type": "string"
            },
            "queue": {
                "type": "string"
            },
            "payload": {
                "type": "object",
                "patternProperties": {
                    ".*": {
                        "type": [
                            "string",
                            "number"
                        ],
                    }
                }
            },
        },
        "required": ["name", "expression", "queue"],
        "additionalProperties": False
        }


    Example::

        { "name": "test",
          "expression": ".greeting | test( "hello" )",
          "queue": "outbox",
          "payload": {
            "@tmp.some.key": 1,
          }
        }

    Disk level conditions
    ---------------------

    The directory <location> contains the conditions in YAML format. One
    condition is one file.  Files not having '.yaml' extension are ignored.

    This directory is monitored for changes and automatically reloaded
    whenever something changes.

    The rules should have following format:

    JSON-schema::

        {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string"
            },
            "queue": {
                "type": "string"
            },
            "payload": {
                "type": "object",
                "patternProperties": {
                    ".*": {
                        "type": [
                            "string",
                            "number"
                        ],
                    }
                }
            },
        },
        "required": ["expression", "queue"],
        "additionalProperties": False
        }

    Example::

        queue: nagios
        expression: '.type | test( "nagios" )'

    payload
    -------

    The payload is a dictionary where keys are wishbone event references.


    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - conditions(dict)([])
           |  A dictionary consisting out of expression, queue, payload.

        - location(str)("")
           |  A directory containing rules.  This directory will be monitored
           |  for changes and automatically read for changes.
           |  An empty value disables this functionality.


    Queues:

        - inbox
           |  Incoming events.

        - no_match
           |  Events which did not match at least one rule.
    '''

    def __init__(self, actor_config, selection="@data", conditions=[], location=""):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.disk_conditions = []
        self.condition_read_lock = Semaphore()

    def preHook(self):

        self.kwargs.conditions = self.validateConditions(self.kwargs.conditions)

        if self.kwargs.location == "":
            self.logging.info("No rules directory defined, not reading rules from disk.")
        else:
            self.logging.info("Rules directoy '%s' defined." % (self.kwargs.location))
            self.sendToBackground(self.monitorRuleDirectory)

    def monitorRuleDirectory(self):

        '''
        Loads new rules when changes happen.
        '''

        self.monitor_location = ReadRulesDisk(self.logging, self.kwargs.location)
        self.disk_conditions = self.monitor_location.readDirectory()
        self.logging.info("Read %s rules from disk and %s defined in config." % (len(self.disk_conditions), len(self.kwargs.conditions)))

        while self.loop():
            try:
                fresh_conditions = self.monitor_location.waitForChanges()
                with self.condition_read_lock:
                    if cmp(self.disk_conditions, fresh_conditions) != 0:
                        self.disk_conditions = fresh_conditions
                        self.logging.info("Read %s rules from disk and %s defined in config." % (len(self.disk_conditions), len(self.kwargs.conditions)))
            except Exception as err:
                self.logging.warning("Problem reading rules directory.  Reason: %s" % (err))
                sleep(1)

    def consume(self, event):

        matched = False
        data = event.get(self.kwargs.selection)

        with self.condition_read_lock:
            for condition in self.kwargs.conditions + self.disk_conditions:
                if self.pool.hasQueue(condition["queue"]):
                    try:
                        result = jq(condition["expression"]).transform(data)
                    except Exception as err:
                        self.logging.error("Skipped invalid jq expression '%s'. Reason: %s" % (condition["name"], err.message.replace("\n", " -> ")))
                        continue

                    if isinstance(result, bool):
                        if result:
                            matched = True
                            e = event.clone()
                            if "payload" in condition:
                                for key, value in condition["payload"].iteritems():
                                    e.set(value, key)
                            self.submit(e, self.pool.getQueue(condition["queue"]))
                    else:
                        self.logging.error("Jq expression '%s' does not return a bool therefor it is skipped." % (condition["name"]))
                else:
                    self.logging.warning("Condition '%s' has queue '%s' defined but nothing connected." % (condition["name"], condition["queue"]))

        if not matched:
            self.submit(event, self.pool.queue.no_match)


    def validateConditions(self, conditions):
        '''
        Validates <conditions> whether each condition is valid.
        Returns a list of valid conditions.
        '''

        rules = []
        for condition in conditions:
            try:
                validate(condition, SCHEMA)
            except Exception as err:
                self.logging.error("Rule '%s' is invalid therefor skipped. Reason: %s" % (condition, err.message))
            finally:
                rules.append(condition)
        return rules


class ReadRulesDisk():

    '''
    Loads jq rules from a directory and monitors the directory for
    changes.

    Parameters:

        directory(string):   The directory to load rules from.
                            default: rules/

    '''

    def __init__(self, logger, directory="rules/"):
        self.logging = logger
        self.directory = directory

        if not os.access(self.directory, os.R_OK):
            raise Exception("Directory '%s' is not readable. Please verify." % (self.directory))

        self.fd = inotify.init()
        self.wb = inotify.add_watch(self.fd, self.directory, inotify.IN_CLOSE_WRITE + inotify.IN_CREATE + inotify.IN_DELETE + inotify.IN_MODIFY + inotify.IN_MOVE)
        self.logging.info("Monitoring directory '%s' for changes" % (directory))

    def createDir(self):

        if os.path.exists(self.kwargs.location):
            if not os.path.isdir(self.kwargs.location):
                raise Exception("%s exists but is not a directory" % (self.kwargs.location))
            else:
                self.logging.info("Directory %s exists so I'm using it." % (self.kwargs.location))
        else:
            self.logging.info("Directory %s does not exist so I'm creating it." % (self.kwargs.location))
            os.makedirs(self.kwargs.location)

    def readDirectory(self):

        return self.__readDirectory()

    def waitForChanges(self):

        inotify.get_events(self.fd)
        return self.readDirectory()

    def __readDirectory(self):
        '''Reads the content of the given directory and creates a dict
        containing the rules.'''

        rules = []
        for filename in glob("%s/*.yaml" % (self.directory)):
            try:
                with open(filename, 'r') as f:
                    rule_name = os.path.basename(filename).rstrip(".yaml")
                    rule = yaml.load("".join(f.readlines()))
                    try:
                        validate(rule, SCHEMA_DISK)
                    except Exception as err:
                        self.logging.warning("Rule %s not valid. Skipped. Reason: %s" % (filename, err.message))
                    else:
                        rule["name"] = rule_name
                        rules.append(rule)
            except ParserError as err:
                self.logging.warning("Failed to parse file %s.  Please validate the YAML syntax in a parser." % (filename))
            except IOError as err:
                self.logging.warning("Failed to read %s.  Reason: %s" % (filename, err))
            except Exception as err:
                self.logging.warning("Unknown error parsing file %s.  Skipped.  Reason: %s." % (filename, err))

        return rules

