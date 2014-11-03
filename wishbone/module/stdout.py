#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stdout.py
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
from gevent import sleep
from os import getpid


class Format():

    def __init__(self, complete, counter, pid):
        self.countervalue = -1
        if complete:
            self.complete = self.__returnComplete
        else:
            self.complete = self.__returnIncomplete
        if counter:
            self.counter = self.__returnCounter
        else:
            self.counter = self.__returnNoCounter
        if pid:
            self.pid_value = getpid()
            self.pid = self.__returnPid
        else:
            self.pid = self.__returnNoPid

    def do(self, event):
        return self.pid(self.counter(self.complete(event)))

    def __returnComplete(self, event):
        return event.raw()

    def __returnIncomplete(self, event):
        return event.last.data

    def __returnCounter(self, event):
        self.countervalue += 1
        return "%s - %s" % (self.countervalue, event)

    def __returnNoCounter(self, event):
        return event

    def __returnNoPid(self, event):
        return event

    def __returnPid(self, event):
        return "PID-%s: %s" % (self.pid_value, event)


class STDOUT(Actor):

    '''**Prints incoming events to STDOUT.**

    Prints incoming events to STDOUT. When <complete> is True,
    the complete event including headers is printed to STDOUT.

    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - complete(bool)(False)
           |  When True, print the complete event including headers.

        - counter(bool)(False)
           |  Puts an incremental number for each event in front
           |  of each event.

        - prefix(str)("")
           |  Puts the prefix in front of each printed event.

        - pid(bool)(False)
           |  Includes the pid of the process producing the output.

        - flush(int)(1)
           |  The interval at which data needs to be flushed.


    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, name, size=100, frequency=1, complete=False, counter=False, prefix="", pid=False, flush=1):
        Actor.__init__(self, name, size, frequency)

        self.complete = complete
        self.counter = counter
        self.prefix = prefix
        self.format = Format(complete, counter, pid)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):
        print ("%s%s" % (self.prefix, self.format.do(event)))
