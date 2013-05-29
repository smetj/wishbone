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

from wishbone.errors import QueueLocked, QueueEmpty
from collections import deque
from gevent.event import Event
from gevent import sleep
from time import time

class WishboneQueue():

    '''A queue used to organize communication messaging between Wishbone Actors.
    '''

    def __init__(self):
        self.__q=deque()
        self.__in=0
        self.__out=0
        self.__cache={}

        self.__getlock=False
        self.__putlock=False

        self.__data_available=Event()
        self.__data_available.clear()

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
                self.__out+=1
                return data
            except IndexError:
                sleep(0.1)
        raise QueueLocked('Locked for outgoing data.')

    def getLock(self):
        '''Locks getting data from queue.'''

        self.__getlock=True

    def getUnlock(self):
        '''Unlocks getting data from queue.'''

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

    def put(self, element):
        '''Puts element in queue.
        '''

        if self.__putlock == True:
            raise QueueLocked('Locked for incoming data.')

        self.__q.append(element)
        self.__in+=1
        self.__data_available.set()

    def putLock(self):
        '''Locks putting data in queue.
        '''

        self.__putlock=True

    def putUnlock(self):
        '''Unlocks putting data in queue.'''

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

    def __rate(self, name, value):
        if not self.__cache.has_key(name):
            self.__cache[name]=(time(), value)
            return 0

        (timex, amount)=self.__cache[name]
        self.__cache[name]=(time(), value)
        #print "%s - %s"%(self.__cache[name][1], amount)
        return (self.__cache[name][1] - amount)/(self.__cache[name][0]-timex)