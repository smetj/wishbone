#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  queue.py
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

from uuid import uuid4
from gevent.queue import Queue as Gevent_Queue
from wishbone.error import QueueFull, QueueEmpty
from time import time
from gevent.queue import Empty, Full
from .wishbonequeue import WishboneQueue


class MemoryQueue(WishboneQueue):

    """A queue used to organize communication messaging between Wishbone Actors.

    Parameters:

        - max_size (int):   The max number of elements in the queue.
                            Default: 1

    When a queue is created, it will drop all messages. This is by design.
    When <disableFallThrough()> is called, the queue will keep submitted
    messages.  The motivation for this is that when is queue is not connected
    to any consumer it would just sit there filled and possibly blocking the
    chain.

    The <stats()> function will reveal whether any events have disappeared via
    this queue.

    """

    def __init__(self, max_size=100):
        self.max_size = max_size
        self.id = str(uuid4())
        self.__q = Gevent_Queue(max_size)
        self.__in = 0
        self.__out = 0
        self.__dropped = 0
        self.__cache = {}

        self.put = self.__fallThrough

    def clean(self):
        """Deletes the content of the queue.
        """
        self.__q = Gevent_Queue(self.max_size)

    def disableFallThrough(self):
        self.put = self.__put

    def dump(self):
        """Dumps the queue as a generator and cleans it when done.
        """

        while True:
            try:
                yield self.get(block=False)
            except QueueEmpty:
                break

    def empty(self):
        """Returns True when queue and unacknowledged is empty otherwise False."""

        return self.__q.empty()

    def enableFallThrough(self):
        self.put = self.__fallThrough

    def get(self, timeout=1):
        """Gets an element from the queue."""

        try:
            e = self.__q.get(timeout=timeout)
        except Empty:
            raise QueueEmpty("Queue is empty.")
        self.__out += 1
        return e

    def size(self):
        """Returns the length of the queue."""

        return self.__q.qsize()

    def stats(self):
        """Returns statistics of the queue."""

        return {
            "size": self.__q.qsize(),
            "in_total": self.__in,
            "out_total": self.__out,
            "in_rate": self.__rate("in_rate", self.__in),
            "out_rate": self.__rate("out_rate", self.__out),
            "dropped_total": self.__dropped,
            "dropped_rate": self.__rate("dropped_rate", self.__dropped),
        }

    def __fallThrough(self, element, timeout=1):
        """Accepts an element but discards it"""

        self.__dropped += 1
        del (element)

    def __put(self, element, timeout=1):
        """Puts element in queue."""

        try:
            self.__q.put(element, timeout=timeout)
            self.__in += 1
        except Full:
            raise QueueFull("Queue full.")

    def __rate(self, name, value):

        if name not in self.__cache:
            self.__cache[name] = {"value": (time(), value), "rate": 0}
            return 0

        (time_then, amount_then) = self.__cache[name]["value"]
        (time_now, amount_now) = time(), value

        if time_now - time_then >= 1:
            self.__cache[name]["value"] = (time_now, amount_now)
            self.__cache[name]["rate"] = (amount_now - amount_then) / (
                time_now - time_then
            )

        return self.__cache[name]["rate"]

    def __repr__(self):

        return "<WishboneQueue::MemoryQueue %s>" % (id(self))
