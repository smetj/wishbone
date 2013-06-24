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

    def createQueue(self, name):
        '''Creates a Queue.
        '''

        try:
            setattr(self.queuepool, name, WishboneQueue())
            self.logging.info('Created module queue named %s.'%(name))
        except Exception as err:
            self.logging.warn('I could not create the queue named %s. Reason: %s'%(name, err))

    def getLog(self):
        '''Retrieves a log from the log queue.'''

        return self.logging.logs.get()

    def waitUntilData(self, queue="inbox"):
        '''Blocks untill data arrives in queue'''

        getattr(self.queuepool, queue).waitUntilData()