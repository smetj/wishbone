#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  diskin.py
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

from wishbone import Actor
from wishbone.error import QueueFull, QueueEmpty

import cPickle as pickle
from gevent.fileobject import FileObjectThread
from gevent import spawn, sleep
from os import remove
import glob


class DiskIn(Actor):

    '''**Reads messages from a disk buffer.**


    Parameters:

        -   name(str)
            The name of the module.

        -   size(int)
            The default max length of each queue.

        -   frequency(int)
            The frequency in seconds to generate metrics.

        - directory(str):   The directory to write data to.

    Queues:

        - outbox:    Incoming events.
    '''

    def __init__(self, name, size=100, frequency=1, directory="./"):
        Actor.__init__(self, name, size, frequency)
        self.name = name
        self.directory = directory

        self.pool.createQueue("outbox")

    def preHook(self):
        spawn(self.monitorDirectory)

    def monitorDirectory(self):
        while self.loop:
            self.processDirectory()
            sleep(0.5)

    def processDirectory(self):
        for filename in glob.glob("%s/*.ready" % (self.directory)):
            self.readFile(filename)

    def readFile(self, filename):
        if filename.endswith("ready") and self.loop():
            with open(filename, "r") as output_file:
                self.logging.debug("Reading file %s" % filename)
                f = FileObjectThread(output_file)
                while self.loop():
                    try:
                        event = pickle.load(f)
                        while self.loop():
                            try:
                                self.pool.queue.outbox.put(event)
                                break
                            except QueueFull:
                                self.pool.queue.outbox.waitUntilFree()
                    except EOFError:
                        break

            remove(filename)
