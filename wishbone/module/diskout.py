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

from wishbone.error import QueueFull
from wishbone import Actor
from gevent.os import make_nonblocking
from gevent import sleep
from uuid import uuid4
import os
import cPickle as pickle


class DiskOut(Actor):

    '''**Writes complete messages to a disk buffer.**

    Persists complete incoming messages to disk.

        Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - directory(str)("./)
           |  The directory to write data to.

        - interval(int)(10)
           |  The time in seconds to flush the queue to disk.


    Queues:

        - inbox
           |  Incoming events.

    '''

    def __init__(self, actor_config, selection="@data", directory="./", interval=10):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.pool.createQueue("disk")
        self.pool.queue.disk.disableFallThrough()

        self.__flush_lock = False

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
            except QueueFull:
                self.flushDisk()

    def flushDisk(self):

        if self.pool.queue.disk.size() > 0 and not self.__flush_lock:
            self.__flush_lock = True
            i = str(uuid4())
            try:
                with open(r"%s/%s.%s.writing" % (self.kwargs.directory, self.name, i), "wb") as output_file:
                    make_nonblocking(output_file)
                    size = self.pool.queue.disk.size()
                    for event in self.pool.queue.disk.dump():
                        pickle.dump(event, output_file)
            except Exception as err:
                self.logging.error("Failed to write file '%s' to '%s'.  Reason: '%s'." % (self.name, self.kwargs.directory, err))
                try:
                    os.remove("%s/%s.%s.writing" % (self.kwargs.directory, self.name, i))
                except Exception as err:
                    self.logging.debug("No file %s/%s.%s.writing to remove" % (self.kwargs.directory, self.name, i))
                self.submit(event, self.pool.queue.disk)
            else:
                os.rename("%s/%s.%s.writing" % (self.kwargs.directory, self.name, i), "%s/%s.%s.ready" % (self.kwargs.directory, self.name, i))
                self.logging.info("Wrote %s events to file %s/%s.%s.ready" % (size, self.kwargs.directory, self.name, i))
            self.__flush_lock = False

    def __flushTimer(self):

        while self.loop():
            sleep(self.kwargs.interval)
            self.flushDisk()