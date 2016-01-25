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


from wishbone import Actor
from jq import jq
from jsonschema import validate


class JQ(Actor):

    '''**Evaluates a data structure against jq expressions.**

    Evalutes (JSON) data structures against a set of jq expressions to decide
    which queue to forward the event to.

    An expression is a dictionary with following structure:

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

    For example:

    { "name": "test",
      "expression": ".greeting | test( "hello" )",
      "queue": "outbox",
      "payload": {
        "one": 1,
        "two": 2,
      }
     }

    The payload dictionary's keys are Wishbone event references.

    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - conditions(dict)([])
           |  A dictionary consisting out of expression, queue, payload.

        - conditions_directory(str)("./rules")
           |  A directory containing rules.  This directory will be monitored
           |  for changes and automatically read for changes.


    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, actor_config, selection="@data", conditions=[], conditions_directory="./"):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.disk_conditions = []

    def preHook(self):

        self.kwargs.conditions = self.validateConditions(self.kwargs.conditions)

    def consume(self, event):

        data = event.get(self.kwargs.selection)

        for condition in self.kwargs.conditions + self.disk_conditions:
            if self.pool.hasQueue(condition["queue"]):
                result = jq(condition["expression"]).transform(data)
                if isinstance(result, bool):
                    if result:
                        e = event.clone()
                        if "payload" in condition:
                            for key, value in condition["payload"].iteritems():
                                e.set(value, key)
                        self.submit(e, self.pool.getQueue(condition["queue"]))
                else:
                    self.logging.error("Jq expression '%s' does not return a bool therefor it is skipped." % (condition["name"]))
            else:
                self.logging.error("Condition '%s' has queue '%s' defined but nothing connected." % (condition["name"], condition["queue"]))


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
