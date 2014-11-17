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
from wishbone.error import QueueFull

import cPickle as pickle
from gevent.fileobject import FileObjectThread
from gevent.event import Event
from gevent import spawn, sleep
import os
from uuid import uuid4


class DiskOut(Actor):

    '''**Writes messages to a disk buffer.**

    Persists incoming messages to disk.

        Parameters:

        - directory(str)
           |  The directory to write data to.

        - interval(int)
           |  The time in seconds to flush the queue to disk.


    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, actor_config, directory="./", interval=10):
        Actor.__init__(self, actor_config)

        self.directory = directory
        self.interval = interval

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.pool.createQueue("disk")
        self.pool.queue.disk.disableFallThrough()

        self.__flush_lock = Event()
        self.__flush_lock.set()

    def preHook(self):

        self.createDir()
        spawn(self.__flushTimer)

    def createDir(self):

        if os.path.exists(self.directory):
            if not os.path.isdir(self.directory):
                raise Exception("%s exists but is not a directory" % (self.directory))
            else:
                self.logging.info("Directory %s exists so I'm using it." % (self.directory))
        else:
            self.logging.info("Directory %s does not exist so I'm creating it." % (self.directory))
            os.makedirs(self.directory)

    def consume(self, event):

        while self.loop():
            try:
                self.pool.queue.disk.put(event)
                break
            except QueueFull as err:
                self.__flush_lock.wait()
                self.flushDisk()
                err.waitUntilEmpty()

    def flushDisk(self):

        self.__flush_lock.clear()
        if self.pool.queue.disk.size() > 0:

            i = str(uuid4())
            filename = "%s/%s.%s.writing" % (self.directory, self.name, i)
            self.logging.debug("Flusing %s messages to %s." % (self.pool.queue.disk.size(), filename))

            try:
                with open(r"%s/%s.%s.writing" % (self.directory, self.name, i), "wb") as output_file:
                    f = FileObjectThread(output_file)
                    for event in self.pool.queue.disk.dump():
                        pickle.dump(event, f)
            except Exception as err:
                os.rename("%s/%s.%s.writing" % (self.directory, self.name, i), "%s/%s.%s.failed" % (self.directory, self.name, i))
            else:
                os.rename("%s/%s.%s.writing" % (self.directory, self.name, i), "%s/%s.%s.ready" % (self.directory, self.name, i))
        self.__flush_lock.set()

    def __flushTimer(self):

        while self.loop():
            sleep(self.interval)
            self.__flush_lock.wait()
            self.flushDisk()
