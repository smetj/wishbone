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

from mx.Stack import Stack, EmptyError
from gevent.event import Event
from gevent import spawn, sleep
from itertools import count
from time import time

class WishboneQueue():

    '''A queue used to organize communication messaging between Wishbone Actors.

    Parameters:

        - ack(bool):            Each consumed message has to be acknowledged.
                                (default False)

        - shrink_interval(int)  Compacts the queue every X seconds.
                                (default 10)

        - max (int)             Defines the maximum size of the queue. A value
                                of 0 means unlimited.
                                (default 0)

    '''

    def __init__(self, ack=False, shrink_interval=10, max=0):
        self.__q=Stack()
        self.__acktable={}
        self.__ackticket=count()
        self.__in=0
        self.__out=0
        self.__ack=0
        self.__shrink_interval=int(shrink_interval)
        self.__cache={}

        self.__getlock=Event()
        self.__getlock.set()
        self.__getblock=Event()
        self.__getblock.set()

        self.__putlock=Event()
        self.__putlock.set()
        self.__putblock=Event()
        self.__putblock.set()

        self.__data_available=Event()
        if ack == True:
            self.get=self.__getAck
        else:
            self.get=self.__getNoAck
        spawn(self.__shrinkMonitor,self.__shrink_interval)

    def put(self, element):
        '''Puts element in queue.
        '''
        self.__putblock.wait()

        if not self.__putlock.isSet():
            raise Exception('Queue is locked.')
        else:
            self.__q.push(element)
            self.__in+=1
            self.__data_available.set()

    def get(self):
        '''Gets an element from the queue.

        Points to self.__getNoAck or self.__getAck depending on init.'''

        pass

    def getLock(self):
        '''Locks getting data from queue.'''

        self.__getlock.clear()

    def getUnlock(self):
        '''Unlocks getting data from queue.'''

        self.__getlock.set()
        spawn(self.__shrinkMonitor,self.__shrink_interval)

    def getBlock(self):
        '''Blocks on getting data from queue.'''

        self.__getblock.clear()

    def getUnblock(self):
        '''Unblocks getting data from queue.'''

        self.__getblock.set()

    def putLock(self):
        '''Locks putting data in queue.
        '''

        self.__putlock.clear()

    def putUnlock(self):
        '''Unlocks putting data in queue.'''

        self.__putlock.set()

    def putBlock(self):
        '''Blocks putting data in queue.
        '''

        self.__putblock.clear()

    def putUnblock(self):
        '''Unblocks putting data in queue.'''

        self.__putblock.set()

    def __getNoAck(self, timeout=None):
        '''Gets an element from the queue.

        Blocks when empty until an element is returned.'''

        if not self.__getlock.isSet():
            raise Exception ("Queue is locked for outgoing data.")

        while self.__getlock.isSet():
            try:
                data = self.__q.pop()
                self.__out+=1
                return data
            except EmptyError:
                self.__data_available.clear()
                self.__data_available.wait(1)

    def __getAck(self):
        '''Gets an element from the queue with acknowledgement.

        Blocks when empty until an element is returned.'''
        if not self.__getlock.isSet():
            raise Exception ("Queue is locked for outgoing data.")

        while self.__getlock.isSet():
            try:
                data = self.__q.pop()
                ticket=next(self.__ackticket)
                self.__acktable[ticket]=data
                return (data, ticket)
            except EmptyError:
                self.__data_available.clear()
                raise EmptyError

    def acknowledge(self, ticket):
        '''Acknowledges a previously consumed element.'''

        try:
            del(self.__acktable[ticket])
        except:
            return False

        self.__out+=1
        self.__ack+=1
        return True

    def cancel(self, ticket):
        '''Cancels an acknowledgement ticket.

        Returns the previously consumed element back to the queue.'''

        try:
            data = self.__acktable[ticket]
            del(self.__acktable[ticket])
            self.__q.push(data)
            return True
        except:
            return False

    def cancelAll(self):
        '''Cancels all acknowledgement tickets.

        All unacknowledged elements are send back to the queue.
        '''

        for event in self.__acktable.keys():
            self.__q.push(self.__acktable[event])
            sleep()
        self.__acktable={}

    def dump(self):
        '''Dumps and returns the queue in tuple format.
        '''

        for event in self.__q.as_tuple():
            yield event
            sleep()

    def lock(self):
        '''Sets queue in locked state.

        When in locked state, elements can not be added or consumed.'''

        self.getLock()
        self.putLock()

    def isLocked(self):
        '''Returns whether the queue is in locked or unlocked state.

        True means locked, False means unlocked.'''

        return (not self.__getlock.isSet(), not self.__putlock.isSet())

    def unlock(self):
        '''Sets queue in unlocked state.

        When in unlocked state, elements can be added or consumed.'''

        self.getUnlock()
        self.putUnlock()

    def size(self):
        '''Returns a tuple of the queue and unacknowledged the size of the queue.'''
        return (len(self.__q),len(self.__acktable))

    def empty(self):
        '''Returns True when queue and unacknowledged is empty otherwise False.'''

        if len(self.__q) > 0:
            return False
        else:
            return True

    def clear(self):
        '''Clears the queue.'''
        self.__q.clear()

    def stats(self):
        '''Returns statistics of the queue.'''
        return { "size":len(self.__q),
            "in_total":self.__in,
            "out_total":self.__out,
            "ack_total":self.__ack,
            "in_rate": self.__rate("in_rate",self.__in),
            "out_rate": self.__rate("out_rate",self.__out),
            "ack_rate":self.__rate("ack_rate",self.__ack)}

    def shrink(self):
        '''Can be called to shrink the allocated memory to the minimum required to hold the
        number of elments currently in the Stack.

        http://www.egenix.com/products/python/mxBase/mxStack/doc/#_Toc293606071
        '''
        self.__q.resize()

    def waitUntilData(self):
        '''Blocks untill data is available'''

        self.__data_available.wait(timeout=1)

    def __rate(self, name, value):
        if not self.__cache.has_key(name):
            self.__cache[name]=(time(), value)
            return 0

        (timex, amount)=self.__cache[name]
        self.__cache[name]=(time(), value)
        #print "%s - %s"%(self.__cache[name][1], amount)
        return (self.__cache[name][1] - amount)/(self.__cache[name][0]-timex)

    def __shrinkMonitor(self, interval):

        '''Greenlet which runs in background executing self.shrink() at the
        chosen interval.'''

        while self.isLocked() == False:
            self.shrink()
            sleep(interval)


