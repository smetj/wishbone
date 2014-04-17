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

from wishbone.tools import WishboneQueue

class QueueFunctions():

    def __init__(self):
        from wishbone.tools import QueuePool
        self.queuepool=QueuePool()

    def createQueue(self, name, max_size=0):
        '''Creates a queue in <self.queuepool> named <name> with a size of <max_size>'''

        try:
            setattr(self.queuepool, name, WishboneQueue(max_size))
            self.logging.debug('Created module queue named %s with max_size %s.'%(name, max_size))
        except Exception as err:
            self.logging.warn('I could not create the queue named %s. Reason: %s'%(name, err))

    def deleteQueue(self, name):
        '''Deletes the <name> queue from <self.queuepool>.'''

        try:
            del self.queuepool.__dict__[name]
            self.logging.debug('Deleted module queue named %s.'%(name))
        except Exception as err:
            self.logging.warn('Problem deleting queue %s.  Reason: %s.'%(name, err))