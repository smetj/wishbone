#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  humanlogformat.py
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
from wishbone.event import Log
from time import strftime, localtime
import os
import sys


class HumanLogFormat(Actor):

    '''**Formats Wishbone log events.**

    Logs are formated from the internal wishbone format into a more
    pleasing human readable format suited for STDOUT or a logfile.

    Internal Wishbone format:

    (6, 1367682301.430527, 3342, 'Router', 'Received SIGINT. Shutting down.')

    Sample output format:

    2013-08-04T19:54:43 pid-3342 informational dictgenerator: Initiated
    2013-08-04T19:54:43 pid-3342 informational metrics_null: Started


    Parameters:

        n/a

    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, colorize=True, ident=None):
        Actor.__init__(self, actor_config)
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

        if self.kwargs.colorize:
            self.colorize = self.doColorize
        else:
            self.colorize = self.doNoColorize

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

        if self.kwargs.ident is None:
            self.kwargs.ident = os.path.basename(sys.argv[0])

    def consume(self, event):

        if isinstance(event.data, Log):
            log = ("%s %s %s %s: %s" % (
                strftime("%Y-%m-%dT%H:%M:%S", localtime(event.data.time)),
                "%s[%s]:" % (self.kwargs.ident, event.data.pid),
                self.levels[event.data.level],
                event.data.module,
                event.data.message))
            event.data = self.colorize(log, event.data.level)
            self.submit(event, self.pool.queue.outbox)
        else:
            raise Exception("Incoming data needs to be of type <wishbone.event.Log>. Dropped event.")

    def doColorize(self, message, level):
        return self.colors[level] + message + "\x1B[0m"

    def doNoColorize(self, message, level):
        return message
