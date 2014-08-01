#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  testevent.py
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
from wishbone.error import QueueFull
from gevent import spawn, sleep


class TestEvent(Actor):

    '''**Generates a test event at the chosen interval.**


    Events have following format:

        { "header":{}, "data":"test" }

    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - interval(float)(1)
           |  The interval in seconds between each generated event.
           |  A value of 0 means as fast as possible.

        - message(string)("test")
           |  The content of the test message.

        - numbered(bool)
           |  When true, appends a sequential number to the end.


    Queues:

        - outbox
           |  Contains the generated events.
    '''

    def __init__(self, name, size=100, frequency=1, interval=1, message="test", numbered=False):
        Actor.__init__(self, name, size, frequency)
        self.name = name
        self.interval = interval
        self.message = message
        self.numbered = numbered

        self.pool.createQueue("outbox")

        if interval == 0:
            self.sleep = self.__doNoSleep
        else:
            self.sleep = self.__doSleep

        if numbered:
            self.number = self.__doNumber
            self.n = 0
        else:
            self.number = self.__doNoNumber

    def preHook(self):
        self.threads.spawn(self.produce)

    def produce(self):

        while self.loop():
            event = {"header": {}, "data": "%s%s" % (self.message, self.number())}
            while self.loop():
                try:
                    self.pool.queue.outbox.put(event)
                    break
                except QueueFull as err:
                    err.waitUntilFree()
            self.sleep()

        self.logging.info("Stopped producing events.")

    def __doSleep(self):
        sleep(self.interval)

    def __doNoSleep(self):
        pass

    def __doNumber(self):
        self.n += 1
        return "_%s" % (self.n)

    def __doNoNumber(self):
        return ""
