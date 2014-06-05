#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#
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

from uuid import uuid4
from collections import deque
from wishbone.error import QueueLocked, QueueEmpty, QueueFull
from gevent.event import Event
from gevent import sleep
from gevent.pool import Group
from time import time

class Container():
    pass

class QueuePool():

    def __init__(self, size):
        self.__size=size
        self.queue = Container()
        self.queue.metrics = Queue(size)
        self.queue.logs = Queue(size)
        self.queue.success = Queue(size)
        self.queue.failed = Queue(size)

    def listQueues(self, names=False, default=True):
        '''returns the list of queue names from the queuepool.

        :param default: When False excludes default queues.

        '''

        if default == True:
            blacklist = []
        else:
            blacklist = [ 'failed', 'success', 'logs', 'metrics' ]

        for m in self.queue.__dict__.keys():
            if m not in blacklist:
                if names == False:
                    yield getattr(self.queue, m)
                else:
                    yield m

    def createQueue(self, name):
        '''Creates a Queue.'''

        if name in [ "metrics", "logs", "success", "failed" ]:
            raise ReservedName

        setattr(self.queue, name, Queue(self.__size))

    def hasQueue(self, name):
        '''Returns trie when queue with <name> exists.'''

        try:
            getattr(self.queue, name)
            return True
        except:
            return False

    def getQueue(self, name):
        '''Convenience funtion which returns the queue instance.'''

        return getattr(self.queue, name)

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
        self.max_size=max_size
        self.id = str(uuid4())
        self.__q=deque()
        self.__in=0
        self.__out=0
        self.__dropped=0
        self.__cache={}

        self.__empty=Event()
        self.__empty.set()

        self.__free=Event()
        self.__free.set()


        self.__full=Event()
        self.__full.clear()

        self.__content=Event()
        self.__content.clear()

        self.put = self.__fallThrough

    def disableFallThrough(self):
        self.put = self.__put

    def dump(self):
        '''Dumps and returns the queue in tuple format.
        '''

        for event in self.__q:
            yield event

    def empty(self):
        '''Returns True when queue and unacknowledged is empty otherwise False.'''

        return self.__q.empty()

    def enableFallthrough(self):
        self.put = self.__fallThrough

    def get(self):
        '''Gets an element from the queue.'''

        try:
            e = self.__q.pop()
        except IndexError:
            self.__empty.set()
            self.__full.clear()
            raise QueueEmpty

        self.__out+=1
        self.__free.set()
        self.__content.clear()
        return e

    def rescue(self, element):

        self.__q.append(element)

    def size(self):
        '''Returns the length of the queue.'''

        return len(self.__q)

    def stats(self):
        '''Returns statistics of the queue.'''

        return { "size":len(self.__q),
            "in_total":self.__in,
            "out_total":self.__out,
            "in_rate": self.__rate("in_rate", self.__in),
            "out_rate": self.__rate("out_rate", self.__out),
            "dropped_total":self.__dropped,
            "dropped_rate":self.__rate("dropped_rate", self.__dropped)
            }

    def waitUntilEmpty(self):
        '''Blocks until the queue is completely empty.'''

        self.__empty.wait()

    def waitUntilFull(self):
        '''Blocks until the queue is completely full.'''

        self.__full.wait()

    def waitUntilFree(self):
        '''Blocks until at least 1 slot it free.'''

        self.__free.wait()

    def waitUntilContent(self):
        '''Blocks until at least 1 slot is taken.'''

        self.__content.wait()

    def __fallThrough(self, element):
        '''Accepts an element but discards it'''

        self.__dropped+=1

    def __put(self, element):
        '''Puts element in queue.'''

        if len(self.__q) == self.max_size:
            self.__empty.clear()
            self.__full.set()
            raise QueueFull

        self.__q.append(element)
        self.__in+=1
        self.__free.clear()
        self.__content.set()

    def __rate(self, name, value):

        if not name in self.__cache:
            self.__cache[name]={"value":(time(), value),"rate":0}
            return 0

        (time_then, amount_then)=self.__cache[name]["value"]
        (time_now, amount_now)=time(), value

        if time_now - time_then >= 1:
            self.__cache[name]["value"]=(time_now, amount_now)
            self.__cache[name]["rate"] = (amount_now - amount_then)/(time_now-time_then)

        return self.__cache[name]["rate"]
