#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fileout.py
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


class File(Actor):

    '''**Writes events to a file**

    Writes incoming events to a file.  Each line represents an event. Keep in
    mind no rotation of the file is done so data is always appended to the end
    of the file.


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - location(str)("./wishbone.out")
           |  The location of the output file.

    Queues:

        - inbox
           |  Incoming messages

    '''

    def __init__(self, name, size, frequency, location="./wishbone.out"):

        Actor.__init__(self, name)
        self.name = name
        self.location = location

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        self.file = open(self.location, "a")

    def consume(self, event):
        self.file.write(str(event["data"]) + "\n")
        self.file.flush()

    def postHook(self):

        self.file.close()
