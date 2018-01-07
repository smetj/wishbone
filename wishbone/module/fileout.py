#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fileout.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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


from wishbone.actor import Actor
from wishbone.module import OutputModule
from gevent.os import make_nonblocking
import arrow


class FileOut(OutputModule):

    '''**Writes events to a file**

    Writes incoming events to a file.  Each line represents an event. Keep in
    mind no rotation of the file is done so data is always appended to the end
    of the file.


    Parameters::

        - selection(str)("data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - location(str)("./wishbone.out")
           |  The location of the output file.

        - timestamp(bool)(False)
           |  If true prepends each line with a ISO8601 timestamp.

    Queues::

        - inbox
           |  Incoming messages

    '''

    def __init__(self, actor_config, selection='data', location="./wishbone.out", timestamp=False):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        if self.kwargs.timestamp:
            self.getTimestamp = self.returnTimestamp
        else:
            self.getTimestamp = self.returnNoTimestamp

        self.file = open(self.kwargs.location, "a")
        make_nonblocking(self.file)

    def consume(self, event):

        if event.isBulk():
            data = event.dumpFieldAsString(self.kwargs.selection)
        else:
            data = str(event.get(self.kwargs.selection))

        self.file.write("%s%s\n" % (self.getTimestamp(), data))
        self.file.flush()

    def returnTimestamp(self):

        return "%s: " % (arrow.now().isoformat())

    def returnNoTimestamp(self):

        return ""

    def postHook(self):

        self.file.close()
