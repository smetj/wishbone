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
from gevent import spawn, sleep, joinall
from gevent import Greenlet
from gevent.event import Event
from gevent.lock import Semaphore
from wishbone.errors import QueueLocked, SetupError, QueueFull

class Consumer():

    def __init__(self, setupbasic=True):
        self.__doConsumes=[]
        self.__block=Event()
        self.__block.clear()

        if setupbasic == True:
            self.__setupBasic()
        self.__greenlet=[]
        self.metrics={}

        self.__enable_consuming=Event()
        self.__enable_consuming.set()

    def start(self):
        '''Starts to execute all the modules registered <self.consume> functions.'''

        self.logging.info("Started")

        for c in self.__doConsumes:
            self.__greenlet.append(spawn(self.__doConsume, c[0], c[1]))
            self.logging.debug('Function %s started to consume queue %s.'%(str(c[0]),str(c[1])))

    def shutdown(self):
        '''Stops each module by making <self.loop> return False and which unblocks <self.block>'''

        if self.__block.isSet():
            self.logging.warn('Already shutdown.')
        else:
            self.logging.info('Shutdown')
            self.__block.set()
            self.queuepool.shutdown()
    stop=shutdown

    def block(self):
        '''Convenience function which blocks untill the actor is in stopped state.'''

        self.__block.wait()

    def registerConsumer(self, fc, q):
        '''Registers <fc> as a consuming function for the given queue <q>.'''

        self.__doConsumes.append((fc, q))

    def loop(self):
        '''Convenience function which returns True until stop() has be been
        called.  A word of caution.  Since we're dealing with eventloops,
        if you use a loop which doesn't have any gevent aware code in it
        then you'll block the event loop.'''

        return not self.__block.isSet()

    def putEvent(self, event, destination):
        '''Convenience function submits <event> into <destination> queue.
        When this fails due to QueueFull or QueueLocked, the function will
        block untill the error state disappeard and will resubmit the event
        after which it will exit.

        Should ideally be used by input modules.
        '''

        while self.loop():
            try:
                destination.put(event)
                break
            except QueueLocked:
                destination.waitUntilPutAllowed()
            except QueueFull:
                destination.waitUntilFreePlace()

    def enableConsuming(self):
        '''Sets a flag which makes the router start executing consume().

        The module will starts/continues to excete the consume() function.'''

        self.__enable_consuming.set()
        self.logging.debug("enableConsuming called. Started consuming.")

    def disableConsuming(self):
        '''Sets a flag which makes the router stop executing consume().

        The module will not process further any events at this point until enableConsuming() is called.'''

        self.__enable_consuming.clear()
        self.logging.debug("disableConsuming called. Stopped consuming.")


    def __doConsume(self, fc, q):
        '''Executes <fc> against each element popped from <q>.
        '''


        while self.loop():
            self.__enable_consuming.wait()
            try:
                event = q.get()
                try:
                    event["header"]
                    event["data"]
                except:
                    self.logging.warn("Invalid event format received from parent. Purged")
                    continue
            except QueueLocked:
                self.logging.debug("Queue %s locked."%(str(q)))
                q.waitUntilGetAllowed()
            else:
                #fc(event)
                try:
                    fc(event)
                except Exception as err:
                    self.logging.warn("Problem executing %s. Sleeping for a second. Reason: %s"%(str(fc),err))
                    q.rescue(event)
                    sleep(1)

        self.logging.info('Function %s has stopped consuming queue %s'%(str(fc),str(q)))

    def __setupBasic(self):
        '''Create in- and outbox and a consumer consuming inbox.'''
        self.createQueue('inbox')
        self.createQueue('outbox')
        self.registerConsumer(self.consume, self.queuepool.inbox)

    def consume(self, event):
        '''Raises error when user didn't define this function in his module.'''

        raise SetupError("You should define a consume function.")