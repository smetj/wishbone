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


class ReadRulesDisk():

    '''
    Loads PySeps rules from a directory and monitors the directory for
    changes.

    Parameters:

        directory(string):   The directory to load rules from.
                            default: rules/
    '''

    def __init__(self, directory="rules/"):
        self.directory = directory
        self.wait = event.Event()
        self.wait.clear()
        self.__rules = {}

        if os.access(self.directory, os.R_OK):
            spawn(self.monitorDirectory)
        else:
            raise Exception(
                "Directory '%s' is not readable. Please verify." % (self.directory))

    def monitorDirectory(self):
        '''Monitors the given directory for changes.'''

        fd = inotify.init()
        wb = inotify.add_watch(
            fd, self.directory, inotify.IN_CLOSE_WRITE + inotify.IN_DELETE)
        self.__rules = self.readDirectory()

        while True:
            self.wait.clear()
            events = inotify.get_events(fd)
            current_rules = self.readDirectory()

            if cmp(current_rules, self.__rules) != 0:
                self.__rules = current_rules
                self.wait.set()

    def readDirectory(self):
        '''Reads the content of the given directory and creates a dict
        containing the rules.'''

        rules = {}
        for filename in glob("%s/*.yaml" % (self.directory)):
            f = open(filename, 'r')
            rules[os.path.basename(filename).rstrip(".yaml")] = yaml.load(
                "\n".join(f.readlines()))
            f.close()

        return rules

    def get(self):
        self.wait.wait()
        return self.__rules
