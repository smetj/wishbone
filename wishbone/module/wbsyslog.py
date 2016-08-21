#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wbsyslog.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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
from wishbone.event import Bulk
import syslog
import sys
import os


class Syslog(Actor):

    '''**Writes log events to syslog.**

    Logevents have following format:

    (6, 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')

    The first value corresponds to the syslog severity level.

    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - level(int)(5)*
           |  The loglevel.

        - ident(str)(<script_name>)*
           |  The syslog id string.
           |  If not provided the script name is used.

    Queues:

        - inbox
           |  incoming events
    '''

    def __init__(self, actor_config, selection="@data", level=5, ident=os.path.basename(sys.argv[0])):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        syslog.openlog("%s[%s]" % (self.kwargs.ident, os.getpid()))

    def consume(self, event):

        if isinstance(event, Bulk):
            for e in event.dump():
                data = e.get(self.kwargs.selection)
                self.__writeLog(data)
        else:
            data = event.get(self.kwargs.selection)
            self.__writeLog(data)

    def __writeLog(self, data):

        if isinstance(data, Log):
            syslog.syslog(data.level, "%s: %s" % (data.module, data.message))
        else:
            syslog.syslog(self.kwargs.level, "%s: %s" % (self.kwargs.ident, str(data)))

    def postHook(self):
        syslog.closelog()
