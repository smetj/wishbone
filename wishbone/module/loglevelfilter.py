#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  loglevelfilter.py
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


class LogLevelFilter(Actor):
    '''**A builtin Wishbone module which filters Wishbone log events.**

        name(str)       :   The name of the module.

        max_level(bool) :   The maximum log level to show.
                            Default: 6
    '''

    def __init__(self, name, max_level=6):
        Actor.__init__(self, name, limit=0)
        self.name=name
        self.max_level=max_level
        self.logging.info("Initiated")

    def consume(self, event):

        if event["data"][0] <= self.max_level:
            self.queuepool.outbox.put(event)