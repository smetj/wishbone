#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  consumer.py
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
from gevent import spawn, sleep, joinall
from gevent import Greenlet
from gevent.event import Event
from gevent.coros import Semaphore
from wishbone.errors import QueueLocked

class Consumer():

    def __init__(self, setupbasic=True, limit=0):
        self.__doConsumes=[]
        self.__block=Event()
        self.__block.clear()
        if setupbasic == True:
            self.__setupBasic()
        self.limit=limit
        if limit == 0:
            self.__doConsume = self.__doSequentialConsume
        else:
            self.__doConsume = self.__doPooledConsume
        self.__greenlet=[]
        self.metrics={}

    def start(self):
        self.logging.info("Started")
        for c in self.__doConsumes:
            self.__greenlet.append(spawn(self.__doConsume, c[0], c[1]))
            self.logging.info('Function %s started to consume queue %s.'%(str(c[0]),str(c[1])))

    def shutdown(self):
        if self.__block.isSet():
            self.logging.warn('Already shutdown.')
        else:
            self.__block.set()
            self.queuepool.shutdown()
            self.logging.info('Shutdown')
    stop=shutdown

    def block(self):
        '''Convenience function which blocks untill the actor is in stopped state.'''
        self.__block.wait()

    def registerConsumer(self, fc, q, pooled=0):
        """Registers <fc> as a consuming function for the given queue <q>."""
        self.__doConsumes.append((fc, q))

    def loop(self):
        '''Convenience funtion which returns True untill stop() has
        been called.'''

        return not self.__block.isSet()

    def __doConsume(self):
        '''Just a placeholder.

        Will be replaced by self.__doInfiniteConsume or
        self.__doPoolConsume depending on init.'''

    def __doSequentialConsume(self, fc, q):

        """Executes <fc> against each element popped from <q>.

        For each popped element <fc> is spawned as a greenlet with the element
        as a variable.  There is no limit on the number of greenthreads
        spawned. """

        while self.loop():
            try:
                event = q.get()
                fc(event)
                # try:
                #     fc(event)
                # except Exception as err:
                #     self.logging.warning("Error executing consume function.  Reason: %s"%(event))
                #     q.rescue(event)
            except QueueLocked:
                sleep(0.1)
            sleep()

        self.logging.info('Function %s has stopped consuming queue %s'%(str(fc),str(q)))

    def __doPooledConsume(self, fc, q):
        """Executes <fc> against each element popped from <q>.

        For each popped element <fc> is spawned as a greenlet with the element
        as a variable.  There is a limit on the number of greenthreads
        spawned.  This is achieved by enabling a putlock on <q> when total
        number of running greenthreads <limit> is defined (using a semaphore)
        and unlocked whenever a slot is free.  Actually this doesn't limit the
        number of allowed greenthreads but it keeps  incoming data to the
        queue artificially limited which as a result controls the number of
        concurrent greenthreads. """

        concurrent = Semaphore(self.limit)

        def executor(fc, event, q, concurrent):
            try:
                fc(event)
            except Exception as err:
                q.rescue(event)
            else:
                q.putUnlock()
            concurrent.release()

        while self.loop():
            try:
                concurrent.acquire()
            except:
                q.putLock()
                concurrent.wait()
            else:
                try:
                    event = q.get()
                except QueueLocked:
                    sleep(0.1)
                else:
                    spawn(executor,fc, event, q, concurrent)
            sleep()

        self.logging.info('Function %s has stopped consuming queue %s'%(str(fc),str(q)))

    def __setupBasic(self):
        '''Create in- and outbox and a consumer consuming inbox.'''
        self.createQueue('inbox')
        self.createQueue('outbox')
        self.registerConsumer(self.consume, self.queuepool.inbox)

    def consume(self, event):
        '''Raises error when user didn't define this function in his module.'''

        raise ("You should define a consume function.")