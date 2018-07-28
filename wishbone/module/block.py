#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  block.py
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
from wishbone.queue import MemoryChannel
from gevent.event import Event
from gevent import sleep, spawn


class Blocker(object):
    def __init__(self, seconds):

        self._max_seconds = seconds

        self.__block = Event()
        self.__block.set()

        self.counter = 0
        self._monitor = spawn(self.monitor)

    def monitor(self):

        while True:
            if self.counter > 0:
                self.__block.clear()
                sleep(1)
                self.counter -= 1
            else:
                self.__block.set()
                sleep(1)

    def reset(self):

        self.counter = self._max_seconds - 1

    def block(self):

        self.__block.wait()


class Block(FlowModule):
    """
    Blocks and unblocks the inbox queue depening on incoming control events.**

    Messages arriving to the `inbox` are simply forwarded to the `outbox`
    queue.

    When events arrive to the `retry` queue the `inbox` queue gets blocked
    preventing further events to arrive to it. The message arriving to the
    `retry` queue are forwarded to the `outbox` queue.

    When one or more events arrive to the `unblock` queue the `inbox` queue
    gets unblocked allowing messages to come in again.  Events submitted to
    the `unblock` queue get dropped.

    Parameters::

        n/a

    Queues::

        - inbox:
           |  Incoming messages

        - retry:
           |  Incoming messages

        - unblock:
           |  Unblocks 'inbox' when events on incoming events.
    """

    def __init__(self, actor_config):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox", MemoryChannel())
        self.pool.createQueue("retry", MemoryChannel())

        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.retry, "retry")

        self.blocker = Blocker(10)

    def consume(self, event):

        self.blocker.block()
        self.submit(event, "outbox")

    def retry(self, event):

        self.logging.debug(
            "Event arrived to the 'retry' Queue. Blocking the 'inbox' queue for 10 seconds."
        )
        self.blocker.reset()
        sleep(1)
        self.submit(event, "outbox")
