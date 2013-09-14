#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       testevent.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone import Actor
from wishbone.tools import LoopContextSwitcher
from wishbone.errors import QueueLocked, QueueFull, SetupError
from wishbone.tools.throttle import SleepThrottle
from gevent import sleep, spawn

class TestEvent(Actor, SleepThrottle):

    '''**A WishBone input module which generates a test event at the chosen interval.**

    This module is only available for testing purposes and has further hardly any use.

    Events have following format:

        { "header":{}, "data":"test" }

    Parameters:

        - name (str):               The instance name when initiated.

        - interval (float):         The interval in seconds between each generated event.
                                    Should have a value >= 0
                                    default: 1

    Queues:

        - outbox:    Contains the generated events.
    '''

    def __init__(self, name, interval=1):
        Actor.__init__(self, name, setupbasic=False)
        SleepThrottle.__init__(self)
        self.createQueue("outbox")
        self.name = name
        if interval < 0:
            raise SetupError ("Interval should be bigger or equal to 0.")
        if interval == 0:
            self.sleep=self.doNoSleep
        else:
            self.sleep=self.doSleep

        self.interval=interval

    def preHook(self):
        spawn(self.go)

    def go(self):
        switcher = self.getContextSwitcher(100, self.loop)
        while switcher.do():
            self.throttle()
            try:
                self.queuepool.outbox.put({"header":{},"data":"test"})
            except (QueueFull, QueueLocked):
                self.queuepool.outbox.waitUntilPutAllowed()
            self.sleep(self.interval)

    def doSleep(self, interval):
        sleep(interval)

    def doNoSleep(self, interval):
        pass