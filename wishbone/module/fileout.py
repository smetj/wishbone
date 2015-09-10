#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fileout.py
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
import arrow


class FileOut(Actor):

    '''**Writes events to a file**

    Writes incoming events to a file.  Each line represents an event. Keep in
    mind no rotation of the file is done so data is always appended to the end
    of the file.


    Parameters:

        - location(str)("./wishbone.out")
           |  The location of the output file.

        - timestamp(bool)(False)
           |  If true prepends each line with a ISO8601 timestamp.

        - complete(bool)(False)
           |  When true dumps the complete event structure.
           |  If not just the payload.

    Queues:

        - inbox
           |  Incoming messages

    '''

    def __init__(self, actor_config, location="./wishbone.out", timestamp=False, complete=False):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        if self.kwargs.timestamp:
            self.getTimestamp = self.returnTimestamp
        else:
            self.getTimestamp = self.returnNoTimestamp

        if self.kwargs.complete:
            self.getData = self.returnComplete
        else:
            self.getData = self.returnDataOnly

        self.file = open(self.kwargs.location, "a")

    def consume(self, event):
        self.file.write("%s%s\n" % (self.getTimestamp(), str(self.getData(event))))
        self.file.flush()

    def returnDataOnly(self, event):
        return event.data

    def returnComplete(self, event):
        return event.raw()

    def returnTimestamp(self):

        return "%s: " % (arrow.now().isoformat())

    def returnNoTimestamp(self):

        return ""

    def postHook(self):

        self.file.close()
