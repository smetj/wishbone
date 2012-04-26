#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  toolkit.py
#  
#  Copyright 2012 Jelle Smet development@smetj.net
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

import logging
from gevent import Greenlet
from gevent.queue import Queue
from copy import deepcopy

class QueueFunctions():

    def sendData(self, data, queue='outbox'):
        '''Submits data to the module outbox, with the goal it will be shuffled by a connector to another module inbox.  By default the queue outbox is chosen'''
        
        if self.checkIntegrity(data):
            getattr (self, queue).put ( data )
        else:
            self.logging.warn('Invalid internal data structure detected. Data is purged. Turn on debugging to see datastructure.')
            self.logging.debug('Invalid data structure: %s' % (data))
    
    def sendRaw(self, data, queue='outbox'):
        '''Allows you to bypass message integrity checking.
        Its usage should be sparse, although it's usefull when you want to send data back to a module as it would have come from the outside world.'''
        
        getattr (self, queue).put ( deepcopy(data) )
            
    def sendCommand(self, data, destination='*', queue='outbox'):
        self.outbox.put( (destination, data) )
        
    def checkIntegrity(self, data):
        if type(data) is dict:
            if len(data.keys()) == 2:
                if data.has_key('header') and data.has_key('data'):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
                

class PrimitiveActor(Greenlet, QueueFunctions):

    def __init__(self, name, block):
        Greenlet.__init__(self)
        self.logging = logging.getLogger( name )
        self.logging.info('Initiated.')
        self.name=name
        self.block = block
        self.inbox = Queue(None)
        self.outbox = Queue(None)
        
    def _run(self):
        self.logging.info('Started.')
        while self.block() == True:
            self.consume(self.inbox.get())
                    
    def consume(self, *args, **kwargs):
        raise Exception ('You have no consume function in your class.')
        
    def command(self, *args, **kwargs):
        self.logging.info('Initiated.')
        self.name=name
        self.block = block
        self.inbox = Queue(None)
        self.outbox = Queue(None)
        
    def _run(self):
        self.logging.info('Started.')
        while self.block() == True:
            self.consume(self.inbox.get())

    def shutdown(self):
        self.logging.info('Shutdown')
