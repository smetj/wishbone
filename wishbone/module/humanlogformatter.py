#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  logformatter.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
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
from time import time


class HumanLogFormatter(Actor):
    '''**A builtin Wishbone module which formats Wishbone log events.**

    Logs are formated from the internal wishbone format into a more
    pleasing human readable format suited for STDOUT or a logfile.

    Internal Wishbone format:

    (6, 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')

    Sample output format:

    2013-08-04T19:54:43 pid-3342 informational dictgenerator: Initiated
    2013-08-04T19:54:43 pid-3342 informational metrics_null: Started


    Parameters:

        name(str)       :   The name of the module.

    '''

    def __init__(self, name):
        Actor.__init__(self, name)
        self.name=name
        self.levels={0:"emergency",1:"alert",2:"critical",3:"error",4:"warning",5:"notice",6:"informational",7:"debug"}

    def consume(self, event):
        event["data"] = ("%s %s %s %s: %s"%(
                strftime("%Y-%m-%dT%H:%M:%S", localtime(event["data"][1])),
                "pid-%s"%(event["data"][2]),
                self.levels[event["data"][0]],
                event["data"][3],
                event["data"][4]))
        self.queuepool.outbox.put(event)