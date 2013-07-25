#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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

from wishbone.errors import QueueLocked, QueueEmpty, QueueFull
from collections import deque
from gevent.event import Event
from gevent import sleep
from time import time

class WishboneQueue():

    '''A queue used to organize communication messaging between Wishbone Actors.

    Parameters:

        - max_size (int):   The max number of elements in the queue.  0 is unlimited
                            Default: 0
    '''

    def __init__(self, max_size=0):
        self.max_size = max_size
        self.__q=deque()
        self.__in=0
        self.__out=0
        self.__cache={}
        self.__last_rate=0

        self.__getlock=False
        self.__getlock_event=Event()
        self.__getlock_event.set()

        self.__putlock=False
        self.__putlock_event=Event()
        self.__putlock_event.set()

        self.__free_place=Event()
        self.__free_place.set()


        self.__data_available=Event()
        self.__data_available.clear()



        if max_size == 0:
            self.put = self.__putNoLimit
        else:
            self.put = self.__putLimit

    def clear(self):
        '''Clears the queue.'''
        self.__q.clear()

    def dump(self):
        '''Dumps and returns the queue in tuple format.
        '''

        for event in self.__q:
            yield event
            #sleep()

    def empty(self):
        '''Returns True when queue and unacknowledged is empty otherwise False.'''

        if len(self.__q) > 0:
            return False
        else:
            return True

    def get(self):
        '''Gets an element from the queue.

        Blocks when empty until an element is returned.'''

        while self.__getlock == False:
            try:
                data = self.__q.popleft()
                self.__free_place.set()
                self.__out+=1
                return data
            except IndexError:
                sleep(0.1)
        raise QueueLocked('Locked for outgoing data.')

    def getLock(self):
        '''Locks getting data from queue.'''

        self.__getlock_event.clear()
        self.__getlock=True

    def getUnlock(self):
        '''Unlocks getting data from queue.'''

        self.__getlock_event.set()
        self.__getlock=False

    def isLocked(self):
        '''Returns whether the queue is in locked or unlocked state.

        True means locked, False means unlocked.'''

        return (self.__getlock, self.__putlock)

    def lock(self):
        '''Sets queue in locked state.

        When in locked state, elements can not be added or consumed.'''

        self.getLock()
        self.putLock()

    def __putNoLimit(self, element):
        '''Puts element in queue.
        '''

        if self.__putlock == True:
            raise QueueLocked('Locked for incoming data.')

        self.__q.append(element)
        self.__in+=1
        self.__data_available.set()

    def __putLimit(self, element):
        '''Puts element in queue.
        '''

        if self.__putlock == True:
            raise QueueLocked('Locked for incoming data.')

        if len(self.__q) == self.max_size:
            self.__free_place.clear()
            raise QueueFull('Queue reached max capacity of %s elements.'%(self.max_size))

        self.__q.append(element)
        self.__in+=1
        self.__data_available.set()

    def putLock(self):
        '''Locks putting data in queue.
        '''

        self.__putlock_event.clear()
        self.__putlock=True

    def putUnlock(self):
        '''Unlocks putting data in queue.'''

        self.__putlock_event.set()
        self.__putlock=False

    def rescue(self, data):
        '''Puts data to the beginning of the queue overriding the lock.'''

        self.__q.appendleft(data)

    def size(self):
        '''Returns a tuple of the queue and unacknowledged the size of the queue.'''
        return len(self.__q)

    def stats(self):
        '''Returns statistics of the queue.'''
        return { "size":len(self.__q),
            "in_total":self.__in,
            "out_total":self.__out,
            "in_rate": self.__rate("in_rate",self.__in),
            "out_rate": self.__rate("out_rate",self.__out)}

    def unlock(self):
        '''Sets queue in unlocked state.

        When in unlocked state, elements can be added or consumed.'''

        self.getUnlock()
        self.putUnlock()

    def waitUntilData(self):
        '''Blocks untill data is available unless queue is locked.'''
        if self.__putlock == True:
            return
        self.__data_available.wait()

    def waitUntilPutAllowed(self):
        '''Blocks until writing data into the queue is allowed again.'''

        self.__putlock_event.wait()

    def waitUntilGetAllowed(self):
        '''Blocks until getting data from the queue is allowed again.'''

        self.__getlock_event.wait()

    def waitUntilFreePlace(self):
        '''Blocks until we have at least 1 slot free in the queue.'''

        self.__free_place.wait()

    def __rate(self, name, value):
        if not name in self.__cache:
            self.__cache[name]=(time(), value)
            return 0

        (time_then, amount_then)=self.__cache[name]
        (time_now, amount_now)=time(), value

        if time_now - time_then >= 1:
            self.__cache[name]=(time_now, amount_now)
            self.__last_rate = (amount_now - amount_then)/(time_now-time_then)

        return self.__last_rate
