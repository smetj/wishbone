#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#
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

from uuid import uuid4
from gevent.queue import Queue as Gevent_Queue
from wishbone.error import QueueEmpty, QueueFull, ReservedName, QueueMissing
from gevent.event import Event
from time import time
from gevent.queue import Empty, Full


class Container():
    pass


class QueuePool():

    def __init__(self, size):
        self.__size = size
        self.queue = Container()
        self.queue.metrics = Queue(size)
        self.queue.logs = Queue(size)
        self.queue.success = Queue(size)
        self.queue.failed = Queue(size)

    def listQueues(self, names=False, default=True):
        '''returns the list of queue names from the queuepool.
        '''

        if default:
            blacklist = []
        else:
            blacklist = ['failed', 'success', 'logs', 'metrics']

        for m in self.queue.__dict__.keys():
            if m not in blacklist:
                if not names:
                    yield getattr(self.queue, m)
                else:
                    yield m

    def createQueue(self, name):
        '''Creates a Queue.'''

        if name in ["metrics", "logs", "success", "failed"]:
            raise ReservedName

        setattr(self.queue, name, Queue(self.__size))

    def hasQueue(self, name):
        '''Returns <True> when queue with <name> exists.'''

        try:
            getattr(self.queue, name)
            return True
        except:
            return False

    def getQueue(self, name):
        '''Convenience funtion which returns the queue instance.'''

        try:
            return getattr(self.queue, name)
        except:
            raise QueueMissing

    def join(self):
        '''Blocks until all queues in the pool are empty.'''
        counter = 0
        for queue in self.listQueues():
            while queue.qsize() != 0:
                sleep(0.2)
                counter += 1
                if counter == 5:
                    break


class Queue():

    '''A queue used to organize communication messaging between Wishbone Actors.

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

    '''

    def __init__(self, max_size=1):
        self.max_size = max_size
        self.id = str(uuid4())
        self.__q = Gevent_Queue(max_size)
        self.__in = 0
        self.__out = 0
        self.__dropped = 0
        self.__cache = {}

        self.put = self.__fallThrough

    def clean(self):
        '''Deletes the content of the queue.
        '''
        self.__q = Gevent_Queue(self.max_size)

    def disableFallThrough(self):
        self.put = self.__put

    def dump(self):
        '''Dumps the queue as a generator and cleans it when done.
        '''

        while True:
            try:
                yield self.get()
            except Empty:
                break

    def empty(self):
        '''Returns True when queue and unacknowledged is empty otherwise False.'''

        return self.__q.empty()

    def enableFallthrough(self):
        self.put = self.__fallThrough

    def get(self):
        '''Gets an element from the queue.'''

        e = self.__q.get()
        self.__out += 1
        return e

    def rescue(self, element):

        self.__q.put(element)

    def size(self):
        '''Returns the length of the queue.'''

        return self.__q.qsize()

    def stats(self):
        '''Returns statistics of the queue.'''

        return {"size": self.__q.qsize(),
                "in_total": self.__in,
                "out_total": self.__out,
                "in_rate": self.__rate("in_rate", self.__in),
                "out_rate": self.__rate("out_rate", self.__out),
                "dropped_total": self.__dropped,
                "dropped_rate": self.__rate("dropped_rate", self.__dropped)
                }

    def __fallThrough(self, element):
        '''Accepts an element but discards it'''

        self.__dropped += 1

    def __put(self, element):
        '''Puts element in queue.'''

        try:
            self.__q.put_nowait(element)
            self.__in += 1
        except Full:
            raise QueueFull("Queue has reached capacity of %s elements" % (self.max_size))

    def __rate(self, name, value):

        if name not in self.__cache:
            self.__cache[name] = {"value": (time(), value), "rate": 0}
            return 0

        (time_then, amount_then) = self.__cache[name]["value"]
        (time_now, amount_now) = time(), value

        if time_now - time_then >= 1:
            self.__cache[name]["value"] = (time_now, amount_now)
            self.__cache[name]["rate"] = (amount_now - amount_then) / (time_now - time_then)

        return self.__cache[name]["rate"]
