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

class QueueFunctions():

    def sendData(self, data, destination='*', queue='outbox'):
        getattr (self, queue).put ( ('data', destination, data) )
            
    def sendCommand(self, data, destination='*'):
        self.outbox.put( ('command', destination, data) )

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
            message = self.inbox.get()
            if message[0] == 'data':
                self.consume(message[1])
            elif message[1] == 'command':
                self.command(message[1])
            else:
                pass
                    
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
            message = self.inbox.get()
            if message[0] == 'data':
                self.consume(message[1])
            elif message[1] == 'command':
                self.command(message[1])
            else:
                pass
