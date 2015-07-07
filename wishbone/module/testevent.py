#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  testevent.py
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
from gevent import sleep


class TestEvent(Actor):

    '''**Generates a test event at the chosen interval.**

    The data field of the test event contains the string "test".


    Parameters:

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

    def __init__(self, actor_config, interval=1, message="test", numbered=False):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("outbox")

    def preHook(self):

        if self.kwargs.interval == 0:
            self.sleep = self.__doNoSleep
        else:
            self.sleep = self.__doSleep

        if self.kwargs.numbered:
            self.generateMessage = self.__doNumber
            self.n = 0
        else:
            self.generateMessage = self.__doNoNumber

        self.sendToBackground(self.produce)

    def produce(self):

        while self.loop():
            event = self.createEvent()
            event.data = self.generateMessage(self.kwargs.message)
            self.submit(event, self.pool.queue.outbox)
            self.sleep()

        self.logging.info("Stopped producing events.")

    def __doSleep(self):
        sleep(self.kwargs.interval)

    def __doNoSleep(self):
        pass

    def __doNumber(self, data):
        self.n += 1
        return "%s %s" % (self.n, data)

    def __doNoNumber(self, data):
        return data
