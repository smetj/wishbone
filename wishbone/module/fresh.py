#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fresh.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from wishbone.actor import Actor
from wishbone.module import FlowModule
from gevent import sleep
from wishbone.event import Event


class Fresh(FlowModule):

    '''**Generates a new event unless an event came through in the last x time.**

    This module forwards events without modifying them. If an event has been
    forwarded it resets the timeout counter back to <timeout>.  If the timeout
    counter reaches zero because no messages have passed through, an event
    with <timeout_payload> is generated and submitted to the module's
    <timeout> queue.  When the a timeout_payload has been sent and the event
    stream recovers, a new event with <recovery_payload> is generated and
    submitted to the <timeout> queue.

    Parameters::

        - timeout_payload(int/float/str/obj/list/...)("timeout")
           |  The data a timeout event contains.

        - recovery_payload(int/float/str/obj/list/...)("recovery")
            |  The data a recovery event contains

        - timeout(int)(60)
           |  The max time in seconds allowed to not to receive events.

        - repeat_interval(int)(60)

           |  The interval time to resend the <payload> event in case
           |  <timeout> has expired and

    Queues::

        - inbox
           |  Incoming events.

        - outbox
           |  Outgoing events.

        - timeout
           |  timeout and recovery events.
    '''

    def __init__(self, actor_config, timeout_payload="timeout", recovery_payload="recovery", timeout=60, repeat_interval=60):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("timeout")
        self.registerConsumer(self.consume, "inbox")
        self._counter = self.kwargs.timeout
        self._incoming = False

    def preHook(self):

        self.sendToBackground(self.countDown)

    def consume(self, event):

        self.submit(event, "outbox")
        self._resetTimeout()

    def countDown(self):

        while self.loop():
            if self._counter > 0:
                self._counter -= 1
                sleep(1)
            else:
                self.logging.info("Timeout of %s seconds expired.  Generated timeout event." % (self.kwargs.timeout))
                self._incoming = False
                while self.loop() and not self._incoming:
                    e = Event()
                    e.set(self.kwargs.timeout_payload)
                    self.submit(e, "timeout")
                    self._sleeper(self.kwargs.repeat_interval)
                self.logging.info("Incoming data resumed. Sending recovery event.")
                e = Event()
                e.set(self.kwargs.recovery_payload)
                self.submit(e, "timeout")

    def _resetTimeout(self):

        self._counter = self.kwargs.timeout
        self._incoming = True

    def _sleeper(self, seconds):

        while self.loop() and seconds > 0 and not self._incoming:
            sleep(1)
            seconds -= 1
