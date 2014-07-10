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

import pickle
from gevent.fileobject import FileObjectThread
from gevent import spawn, sleep
from os import remove
import gevent_inotifyx as inotify
import glob


class DiskIn(Actor):

    '''**Reads messages from a disk buffer.**


    Parameters:

        - name(str):       The instance name when initiated.

        - directory(str):   The directory to write data to.

    Queues:

        - outbox:    Incoming events.
    '''

    def __init__(self, name, size, directory="./"):
        Actor.__init__(self, name, size)
        self.name = name
        self.directory = directory

        self.pool.createQueue("outbox")
        self.pool.queue.outbox.disableFallThrough()

    def preHook(self):
        self.processDirectory()
        fd = inotify.init()
        wd = inotify.add_watch(fd, self.directory, inotify.IN_CLOSE_WRITE)
        spawn(self.watcher, fd)

    def watcher(self, fd):
        while self.loop():
            events = inotify.get_events(fd)
            self.processDirectory()

    def processDirectory(self):
        for filename in glob.glob("%s/*.ready" % (self.directory)):
            self.readFile(filename)

    def readFile(self, filename):
        if filename.endswith("ready"):
            with open(filename, "r") as output_file:
                f = FileObjectThread(output_file)
                for event in pickle.load(f):
                    self.pool.queue.outbox.put(event)
            remove(filename)


