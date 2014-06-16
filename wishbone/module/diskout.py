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
from gevent.fileobject import FileObjectThread
from wishbone.error import QueueFull, QueueEmpty
from gevent.fileobject import FileObjectThread
import pickle
from os import rename


class DiskOut(Actor):
    '''**Writes incoming messges to disk.**

    Persists incoming messages to disk.

    Parameters:

        - name(str):       The instance name when initiated.

        - size(int):       The size of all module queues.

        - directory(str):   The directory to write data to.
    Queues:

        - inbox:    Incoming events.
    '''

    def __init__(self, name, size, directory="./"):
        Actor.__init__(self, name, size)
        self.name = name
        self.directory = directory
        self.pool.createQueue("disk")
        self.pool.queue.disk.disableFallThrough()
        self.registerConsumer(self.consume, "inbox")
        self.counter = 0

    def consume(self, event):

        try:
            self.pool.queue.disk.put(event)
        except QueueFull:
            self.pool.queue.inbox.put(event)
            self.flushDisk()
            self.counter += 1

    def flushDisk(self):

        with open(r"%s/%s.%s.tmp" % (self.directory, self.name, self.counter), "wb") as output_file:
            f = FileObjectThread(output_file)
            self.logging.debug("Flushing to disk.")
            while True:
                try:
                    pickle.dump(self.pool.queue.disk.get(), f)
                except QueueEmpty:
                    f.close()
                    break
        rename("%s/%s.%s.tmp" % (self.directory, self.name, self.counter), "%s/%s.%s" % (self.directory, self.name, self.counter))
