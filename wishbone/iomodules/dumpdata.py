#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dumpdata.py
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


from wishbone.toolkit import QueueFunctions, Block
from gevent import sleep, Greenlet
from itertools import repeat
import logging

class DumpData(QueueFunctions,Block,Greenlet):
    '''**A Wishbone IO module which produces 1 batch of x events.**
    
    Generates 1 time upon initialisation a number of events and places them in the inbox queue.
        
    Parameters:

        - name (str):   The instance name when initiated.
        - amount (int): The number of events to produce.
    
    Queues:
    
        - inbox:       "Incoming" generated data.
    ''' 
   
    def __init__(self, name, amount=100):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.logging = logging.getLogger( name )
        self.name=name
        self.amount=amount
        self.logging.info('Initialiazed.')
            
    def _run(self):
        for _ in repeat(None,self.amount):
            self.putData({"header":{}, "data":"x"},'inbox')
            self.logging.debug('Generated event.')
        while self.block() == True:
            sleep(1)

    def shutdown(self):
        self.logging.info('Shutdown')
