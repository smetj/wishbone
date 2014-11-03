#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  humanlogformat.py
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
from time import strftime, localtime
import os
import sys


class HumanLogFormat(Actor):

    '''**Formats Wishbone log events.**

    Logs are formated from the internal wishbone format into a more
    pleasing human readable format suited for STDOUT or a logfile.

    Internal Wishbone format:

    (6, 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')

    Sample output format:

    2013-08-04T19:54:43 pid-3342 informational dictgenerator: Initiated
    2013-08-04T19:54:43 pid-3342 informational metrics_null: Started


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, name, size=100, frequency=1, colorize=True, ident=None):
        Actor.__init__(self, name, size, frequency)
        self.name = name
        self.levels = {
            0: "emergency",
            1: "alert",
            2: "critical",
            3: "error",
            4: "warning",
            5: "notice",
            6: "informational",
            7: "debug"
        }
        self.colors = {
            0: "\x1B[0;35m",
            1: "\x1B[1;35m",
            2: "\x1B[0;31m",
            3: "\x1B[1;31m",
            4: "\x1B[1;33m",
            5: "\x1B[1;30m",
            6: "\x1B[1;37m",
            7: "\x1B[1;37m"
        }

        if colorize:
            self.colorize = self.doColorize
        else:
            self.colorize = self.doNoColorize

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

        if ident is None:
            self.ident = os.path.basename(sys.argv[0])
        else:
            self.ident = ident

    def consume(self, event):
        log = ("%s %s %s %s: %s" % (
            strftime("%Y-%m-%dT%H:%M:%S", localtime(event.last.data[1])),
            "%s[%s]:" % (self.ident, event.last.data[2]),
            self.levels[event.last.data[0]],
            event.last.data[3],
            event.last.data[4]))
        event.last.data = self.colorize(log, event.last.data[0])
        self.submit(event, self.pool.queue.outbox)

    def doColorize(self, message, level):
        return self.colors[level] + message + "\x1B[0m"

    def doNoColorize(self, message, level):
        pass
