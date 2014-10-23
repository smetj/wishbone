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
import cPickle as pickle
from gevent.fileobject import FileObjectThread
from gevent import spawn, sleep, event
from os import remove
import glob
import os
from time import time


class DiskIn(Actor):

    '''**Reads messages from a disk buffer.**


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - directory(str)
           |  The directory to write data to.

        - idle_trigger(bool)(False)
           |  When True, only reads events when no new events
           |  have been written to disk for at least <idle_time>.


        - idle_time(int)(10)
           |  The time in seconds required that no new events
           |  have been written to disk prior to start to consume
           |  the buffered data.


    Queues:

        - outbox
           |  Incoming events.
    '''

    def __init__(self, name, size=100, frequency=1, directory="./", idle_trigger=False, idle_time=10):
        Actor.__init__(self, name, size, frequency)
        self.name = name
        self.directory = directory
        self.idle_trigger = idle_trigger
        self.idle_time = idle_time
        self.reading = event.Event()
        self.reading.set()
        self.pool.createQueue("outbox")

    def preHook(self):
        self.createDir()
        spawn(self.monitorDirectory)
        spawn(self.diskMonitor)

    def createDir(self):

        if os.path.exists(self.directory):
            if not os.path.isdir(self.directory):
                raise Exception("%s exists but is not a directory" % (self.directory))
            else:
                self.logging.info("Directory %s exists so I'm using it." % (self.directory))
        else:
            self.logging.info("Directory %s does not exist so I'm creating it." % (self.directory))
            os.makedirs(self.directory)

    def monitorDirectory(self):
        while self.loop:
            self.processDirectory()
            sleep(0.5)

    def processDirectory(self):
        for filename in glob.glob("%s/*.ready" % (self.directory)):
            self.reading.wait()
            self.readFile(filename)

    def readFile(self, filename):
        if filename.endswith("ready") and self.loop():
            with open(filename, "r") as output_file:
                self.logging.debug("Reading file %s" % filename)
                f = FileObjectThread(output_file)
                while self.loop():
                    try:
                        event = pickle.load(f)
                        event.setHeaderNamespace(self.name)
                        self.submit(event, self.pool.queue.outbox)
                    except EOFError:
                        break
            remove(filename)

    def diskMonitor(self):
        '''Primitive monitor which checks whether new data is added to disk.'''

        while self.loop():
            try:
                newest = max(glob.iglob("%s/*" % (self.directory)), key=os.path.getmtime)
            except:
                pass
            else:
                if time() - os.path.getctime(newest) >= self.idle_time:
                    self.reading.set()
                else:
                    self.reading.clear()
            sleep(1)