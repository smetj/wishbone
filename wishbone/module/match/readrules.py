#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  readrulesdisk.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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

from gevent import spawn
import gevent_inotifyx as inotify
from gevent import event
from glob import glob
import os
import yaml
from yaml.parser import ParserError


class ReadRulesDisk():

    '''
    Loads PySeps rules from a directory and monitors the directory for
    changes.

    Parameters:

        directory(string):   The directory to load rules from.
                            default: rules/

        logger_object(class): A wishbone logger object.
    '''

    def __init__(self, logger_object, directory="rules/"):
        self.directory = directory
        self.wait = event.Event()
        self.wait.clear()
        self.__rules = {}
        self.logger = logger_object

        if os.access(self.directory, os.R_OK):
            spawn(self.monitorDirectory)
        else:
            raise Exception("Directory '%s' is not readable. Please verify." % (self.directory))

    def monitorDirectory(self):
        '''Monitors the given directory for changes.'''

        fd = inotify.init()
        wb = inotify.add_watch(
            fd, self.directory, inotify.IN_CLOSE_WRITE + inotify.IN_CREATE + inotify.IN_DELETE + inotify.IN_MODIFY + inotify.IN_MOVE)
        self.__rules = self.readDirectory()

        while True:
            self.wait.clear()
            events = inotify.get_events(fd)
            current_rules = self.readDirectory()

            if cmp(current_rules, self.__rules) != 0:
                self.logger.info("New set of rules loaded from disk")
                self.__rules = current_rules
                self.wait.set()

    def readDirectory(self):
        '''Reads the content of the given directory and creates a dict
        containing the rules.'''

        rules = {}
        for filename in glob("%s/*.yaml" % (self.directory)):
            try:
                with open(filename, 'r') as f:
                    key_name = os.path.basename(filename).rstrip(".yaml")
                    rule = yaml.load("".join(f.readlines()))
                    try:
                        self.ruleCompliant(rule)
                    except Exception as err:
                        self.logger.warning("Rule %s not valid. Skipped. Reason: %s" % (filename, err))
                    rules[key_name] = rule
            except ParserError as err:
                self.logger.warning("Failed to parse file %s.  Please validate the YAML syntax in a parser." % (filename))
            except IOError as err:
                self.logger.warning("Failed to read %s.  Reason: %s" % (filename, err))
        return rules

    def get(self):
        self.wait.wait()
        return self.__rules

    def ruleCompliant(self, rule):
        assert isinstance(rule["condition"], list), "Condition needs to be of type list."
        for c in rule["condition"]:
            assert isinstance(c, dict), "An individual condition needs to be of type dict."
        assert isinstance(rule["queue"], list), "Queue needs to be of type list."

