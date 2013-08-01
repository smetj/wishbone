#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  stdout.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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


class Filter(Actor):
    '''*A builtin Wishbone module which formats and filters Wishbone log events.

    Incoming Wishbone log events are tuples with following format:

    ('info', 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')

    Parameters:

        name(str)       :   The name of the module.

        max_level(bool) :   The maximum log level to show.
                            Default: 6
    '''

    def __init__(self, name, max_level=6):
        Actor.__init__(self, name, limit=0)
        self.name=name
        self.max_level=max_level
        self.levels={0:"emergency",1:"alert",2:"critical",3:"error",4:"warning",5:"notice",6:"informational",7:"debug"}
        self.logging.info("Initiated")

    def consume(self, event):
        if event["data"][0] <= self.max_level:
            event["data"] = ("%s %s %s %s: %s"%(
                strftime("%Y-%m-%dT%H:%M:%S", localtime(event["data"][1])),
                "pid-%s"%(event["data"][2]),
                self.levels[event["data"][0]],
                event["data"][3],
                event["data"][4]))
            self.queuepool.outbox.put(event)