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
from gevent.os import make_nonblocking
import os
from gevent.event import Event
from gevent import sleep
from uuid import uuid4
from os import remove


class DiskOut(Actor):

    '''**Writes messages to a disk buffer.**

    Persists incoming messages to disk.

        Parameters:

        - directory(str)("./)
           |  The directory to write data to.

        - interval(int)(10)
           |  The time in seconds to flush the queue to disk.

        - ttl(int)(0)
           |  When event has been written to disk more than <ttl>
           |  it will be forwarded to queue <ttl_exceeded>


    Queues:

        - inbox
           |  Incoming events.

        - ttl_exceeded
           |  Events which passed the module <ttl> times.
    '''

    def __init__(self, actor_config, directory="./", interval=10, ttl=0):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.pool.createQueue("disk")
        self.pool.queue.disk.disableFallThrough()
        self.pool.createQueue("ttl_exceeded")

        self.__flush_lock = False

    def preHook(self):

        self.createDir()
        if self.kwargs.ttl > 0:
            self.validateTTL = self.__doTTL
        else:
            self.validateTTL = self.__doNoTTL

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

        if self.validateTTL(event):
            while self.loop():
                try:
                    self.pool.queue.disk.put(event)
                    break
                except Full:
                    self.flushDisk()
        else:
            self.logging.warning("Event TTL of %s exceeded in transit (%s) moving event to ttl_exceeded queue." % (event.getHeaderValue(self.name, "ttl_counter"), self.kwargs.ttl))
            self.submit(event, self.pool.queue.ttl_exceeded)


    def flushDisk(self):

        if self.pool.queue.disk.size() > 0 and not self.__flush_lock:
            self.__flush_lock = True
            i = str(uuid4())
            filename = "%s/%s.%s.writing" % (self.kwargs.directory, self.name, i)

            try:
                with open(r"%s/%s.%s.writing" % (self.kwargs.directory, self.name, i), "wb") as output_file:
                    make_nonblocking(output_file)
                    self.logging.debug("Flushing %s messages to %s." % (self.pool.queue.disk.size(), filename))
                    for event in self.pool.queue.disk.dump():
                        pickle.dump(event, output_file)
            except Exception as err:
                self.logging.error("Failed to write file '%s' to '%s'.  Reason: '%s'." % (self.name, self.kwargs.directory, err))
                try:
                    remove("%s/%s.%s.writing" % (self.kwargs.directory, self.name, i))
                except Exception as err:
                    self.logging.debug("No file %s/%s.%s.writing to remove" % (self.kwargs.directory, self.name, i))
                self.submit(event, self.pool.queue.disk)
            else:
                os.rename("%s/%s.%s.writing" % (self.kwargs.directory, self.name, i), "%s/%s.%s.ready" % (self.kwargs.directory, self.name, i))
                self.logging.info("Wrote file %s/%s.%s.ready" % (self.kwargs.directory, self.name, i))
            self.__flush_lock = False

    def __flushTimer(self):

        while self.loop():
            sleep(self.kwargs.interval)
            self.flushDisk()

    def __doTTL(self, event):

        try:
            value = event.getHeaderValue(self.name, "ttl_counter")
            value += 1
            event.setHeaderValue("ttl_counter", value)
        except KeyError:
            event.setHeaderValue("ttl_counter", 1)
            value = 1

        if value > self.kwargs.ttl:
            return False
        else:
            return True

    def __doNoTTL(self, event):

        return True