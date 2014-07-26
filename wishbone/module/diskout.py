#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  diskout.py
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
from gevent.event import Event
from gevent import spawn, sleep
from os import rename
from uuid import uuid4


class DiskOut(Actor):

    '''**Writes messages to a disk buffer.**

    Persists incoming messages to disk.

        Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - directory(str)
           |  The directory to write data to.

        - interval(int)
           |  The time in seconds to flush the queue to disk.


    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, name, size=100, frequency=1, directory="./", interval=10):
        Actor.__init__(self, name, size)
        self.name = name
        self.directory = directory
        self.interval = interval

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.pool.createQueue("disk")
        self.pool.queue.disk.disableFallThrough()

        self.counter = 0
        self.__flush_lock = Event()
        self.__flush_lock.set()

    def preHook(self):
        spawn(self.__flushTimer)
        pass

    def consume(self, event):

        try:
            self.pool.queue.disk.put(event)
        except QueueFull:
            self.pool.queue.inbox.put(event)
            self.__flush_lock.wait()
            self.flushDisk()
            self.counter += 1

    def flushDisk(self):

        self.__flush_lock.clear()
        if self.pool.queue.disk.size() > 0:

            i = str(uuid4())
            filename = "%s/%s.%s.%s.writing" % (self.directory, self.name, self.counter, i)
            self.logging.debug("Flusing %s messages to %s." % (self.pool.queue.disk.size(), filename))

            try:
                with open(r"%s/%s.%s.%s.writing" % (self.directory, self.name, self.counter, i), "wb") as output_file:
                    f = FileObjectThread(output_file)
                    for event in self.pool.queue.disk.dump():
                        pickle.dump(event, f)
            except:
                rename("%s/%s.%s.%s.writing" % (self.directory, self.name, self.counter, i), "%s/%s.%s.%s.failed" % (self.directory, self.name, self.counter, i))
            else:
                rename("%s/%s.%s.%s.writing" % (self.directory, self.name, self.counter, i), "%s/%s.%s.%s.ready" % (self.directory, self.name, self.counter, i))
        self.__flush_lock.set()

    def __flushTimer(self):

        while self.loop():
            sleep(self.interval)
            self.__flush_lock.wait()
            self.flushDisk()