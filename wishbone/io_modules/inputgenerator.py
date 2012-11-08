#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       inputgenerator.py
#
#       Copyright 2012 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

import logging
from string import ascii_uppercase, ascii_lowercase, digits
from random import choice, uniform
from wishbone.toolkit import QueueFunctions, Block
from gevent import Greenlet, spawn, sleep
from gevent.queue import Queue

class InputGenerator(Greenlet, QueueFunctions, Block):
    ''' 
    
    A WishBone class which generates random data at different configurable specifications.
    It's primary use is for testing purposes.        
       
    Parameters:
    
        * length:   The maximum length of each random generated message.
                    Default: 100
                    Type: Integer
        
        * interval: The time in seconds between each generated messages.
                    Default: 0.1
                    Type: Integer
        
        * randomize:    Make the interval randomize between 0 and the value of interval.
                        Default: false
                        type: Bool
    '''

    def __init__(self, name, *args, **kwargs):
       
        Greenlet.__init__(self)
        Block.__init__(self)
        self.logging = logging.getLogger( name )
        self.name = name
        self.logging.info ( 'Initiated' )        
        
        self.length=kwargs.get('length',100)
        self.interval=kwargs.get('interval',0.1)
        self.randomize=kwargs.get('randomize',False)
        self.inbox=Queue(None)        
        
    def decode (self, gearman_worker, gearman_job):
        self.logging.debug ('Data received.')
        

    def _run(self):
        self.logging.info('Started')
        while self.block():
            self.sendData({'header':{},'data': ''.join(choice(ascii_uppercase + ascii_lowercase + digits) for x in range(99))}, queue='inbox')            
            self.logging.debug('Data generated.')
            if self.randomize == True:
                sleep(uniform(0,self.interval))
            else:
                sleep(self.interval)
        
    def shutdown(self):
        self.logging.info('Shutdown')
