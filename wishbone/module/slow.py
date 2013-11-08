#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  slow.py
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
from gevent import sleep, spawn

class Slow(Actor):
    '''**Processes an incoming event per X seconds.**

    This module only exists for testing purposes and does not have
    any further use.

    Using this module as and output module it could easily overflow
    the Wishbone instances and trigger any threshold logic available.

    Parameters:

        - name(str):        The name of the module.

        - interval(int):    The time to sleep between each consume().
                            Default: 1

        - flush(int):       The time in seconds after which the inbox
                            is flushed.  0 means never.
                            Default: 0


    Queues:

        - inbox:    outgoing events
    '''

    def __init__(self, name, interval=1, flush=0):
        Actor.__init__(self, name)
        self.name=name
        self.interval=interval
        self.flush_interval=flush

    def preHook(self):
        if self.interval > 0:
            spawn (self.flush)

    def consume(self, event):
        sleep(self.interval)

    def flush(self):
        while self.loop():
            sleep(self.flush_interval)
            self.queuepool.inbox.clear()
            self.logging.info("Queue inbox flushed.")
