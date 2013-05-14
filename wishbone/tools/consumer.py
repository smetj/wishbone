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

class Consumer():

    def __init__(self, setupbasic=True):
        self.__consumers=[]
        self.__block=Event()
        self.__block.clear()
        if setupbasic == True:
            self.__setupBasic()
        self.__greenlet=[]
        self.metrics={}

    def start(self):
        self.logging.info("Started")
        for c in self.__consumers:
            self.__greenlet.append(spawn(self.__consumer, c[0], c[1]))
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

    def registerConsumer(self, fc, q):
        """Registers <fc> as a consuming function for the given queue <q>."""
        self.__consumers.append((fc, q))

    def __consumer(self, fc, q):
        """Consumes makes <fc> consume each event from <q>."""
        while not self.__block.isSet():
            event = q.get()
            if self.__checkIntegrity(event) == True:
                fc(event)
            else:
                self.logging.warn('Invalid internal data structure detected. Data is purged. Turn on debugging to see datastructure.')
                #self.logging.debug('Invalid data structure: %s' % (event))
            sleep()
        self.logging.info('Function %s has stopped consuming queue %s'%(str(fc),str(q)))

    def __setupBasic(self):
        '''Create in- and outbox and a consumer consuming inbox.'''
        self.createQueue('inbox')
        self.createQueue('outbox')
        self.registerConsumer(self.consume, self.queuepool.inbox)

    def __checkIntegrity(self, event):
        '''Checks the integrity of the messages passed over the different queues.

        The format of the messages should be:

        { 'headers': {}, data: {} }'''

        if type(event) is dict:
            if len(event.keys()) == 2:
                if event.has_key('header') and event.has_key('data'):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def consume(self, event):
        '''Raises error when user didn't define this function in his module.'''

        raise ("You should define a consume function.")