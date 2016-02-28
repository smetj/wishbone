#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fresh.py
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
from gevent import sleep
from wishbone.event import Event


class Fresh(Actor):

    '''**Generates a new event unless an event came through in the last x time.**

    This module just forwards events without modifying them. The moment a
    message is forwarded, the time counter is reset to its defined <timeout>
    value. If however the counter expires because no new messages have passed
    through in x time, a new message is generated with the defined <payload>.

    Parameters:

        - payload(int/float/str/obj/list/...)("wishbone")
           |  The data a generated event must contain.

        - key(str)("@data")
           |  The location to store <payload>

        - timeout(int)(60)
           |  The time in seconds Puts an incremental number for each event in front
           |  of each event.

        - payload_queue(str)("timeout")
           |  The name of the queue to submit the newly generated event to.

    Queues:

        - inbox
           |  Incoming events.

        - inbox
           |  Incoming events.

        - <payload_queue>
           |  Newly generated events due to timeout.
    '''

    def __init__(self, actor_config, payload="wishbone", key="@data", timeout=60, payload_queue="timeout"):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue(self.kwargs.payload_queue)
        self.registerConsumer(self.consume, "inbox")
        self._counter = self.kwargs.timeout

    def preHook(self):

        self.sendToBackground(self.countDown)

    def consume(self, event):

        self.submit(event, self.pool.queue.outbox)
        self._resetTimeout()

    def countDown(self):

        while self.loop():
            if self._counter > 0:
                self._counter -= 1
                sleep(1)
            else:
                e = Event()
                e.set(self.kwargs.payload, self.kwargs.key)
                self.submit(e, getattr(self.pool.queue, self.kwargs.payload_queue))
                self.logging.info("Timeout of %s seconds expired.  Generting event and submit to queue %s." % (self.kwargs.timeout, self.kwargs.payload_queue))
                self._resetTimeout()

    def _resetTimeout(self):

        self._counter = self.kwargs.timeout
