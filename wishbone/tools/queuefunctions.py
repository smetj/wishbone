#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  queuefunctions.py
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

from wishbone.tools import WishboneQueue

class QueueFunctions():

    def __init__(self):
        from wishbone.tools import QueuePool
        self.queuepool=QueuePool()

    def createQueue(self, name, ack=False):
        '''Creates a Queue.

        When ack is defined it means each consumed event has to be acknowledged.
        This is not implemented yet.'''

        try:
            setattr(self.queuepool, name, WishboneQueue(ack))
            self.logging.info('Created module queue named %s.'%(name))
        except Exception as err:
            self.logging.warn('I could not create the queue named %s. Reason: %s'%(name, err))

    def getLog(self):
        '''Retrieves a log from the log queue.'''

        return self.logging.logs.get()

    def createEvent(self, data, header={}, queue="outbox"):
        '''Produces an event to the requested queue.

        Blocks untill the queue is in unlocked state.'''

        getattr (self.queuepool, queue).put({"header":header, "data":data})

    def sendEvent(self, event, queue="outbox"):
        '''Sends a raw event to the requested queue.'''

        getattr (self.queuepool, queue).put(event)

    def getEvent(self, queue="inbox"):
        '''Consumes an event from the requested queue.

        Blocks untill the queue is in unlocked state.'''

        return getattr (self.queuepool, queue).get()

    def acknowledgeEvent(self, ticket, queue="outbox"):
        '''Acknowledges event.'''

        getattr (self.queuepool, queue).acknowledge(ticket)

    def cancelEvent(self, ticket, queue="outbox"):
        '''Cancels event.'''

        getattr (self.queuepool, queue).cancel(ticket)

    def waitUntilData(self, queue="inbox"):
        '''Blocks untill data arrives in queue'''

        getattr(self.queuepool, queue).waitUntilData()