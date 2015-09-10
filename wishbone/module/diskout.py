#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  diskout.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
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
from gevent.fileobject import FileObjectPosix
from gevent.event import Event
from gevent import sleep
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

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.pool.createQueue("disk")
        self.pool.queue.disk.disableFallThrough()

        self.__flush_lock = Event()
        self.__flush_lock.set()

    def preHook(self):

        self.createDir()
        self.sendToBackground(self.__flushTimer)

    def createDir(self):

        if os.path.exists(self.kwargs.directory):
            if not os.path.isdir(self.kwargs.directory):
                raise Exception("%s exists but is not a directory" % (self.kwargs.directory))
            else:
                self.logging.info("Directory %s exists so I'm using it." % (self.kwargs.directory))
        else:
            self.logging.info("Directory %s does not exist so I'm creating it." % (self.kwargs.directory))
            os.makedirs(self.kwargs.directory)

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
            filename = "%s/%s.%s.writing" % (self.kwargs.directory, self.name, i)
            self.logging.debug("Flusing %s messages to %s." % (self.pool.queue.disk.size(), filename))

            try:
                with open(r"%s/%s.%s.writing" % (self.kwargs.directory, self.name, i), "wb") as output_file:
                    # f = FileObjectPosix(output_file)
                    for event in self.pool.queue.disk.dump():
                        pickle.dump(event, output_file)
            except Exception as err:
                self.logging.error("Failed to write file '%s' to '%s'.  Reason: '%s'." % (self.name, self.kwargs.directory, err))
                os.rename("%s/%s.%s.writing" % (self.kwargs.directory, self.name, i), "%s/%s.%s.failed" % (self.kwargs.directory, self.name, i))
            else:
                os.rename("%s/%s.%s.writing" % (self.kwargs.directory, self.name, i), "%s/%s.%s.ready" % (self.kwargs.directory, self.name, i))
                self.logging.info("Wrote file %s/%s.%s.ready" % (self.kwargs.directory, self.name, i))

        self.__flush_lock.set()

    def __flushTimer(self):

        while self.loop():
            sleep(self.kwargs.interval)
            self.__flush_lock.wait()
            self.flushDisk()
