#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       stdout.py
#       
#       Copyright 2013 Jelle Smet development@smetj.net
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

from wishbone.toolkit import PrimitiveActor


class STDOUT(PrimitiveActor):
    '''**The STDOUT Wishbone module is a minimal module which prints each incoming
    event to STDOUT**
    
    After printing the content of the events to STDOUT they are put into the outbox
    queue unless otherwise defined using the purge parameter.  When the complete
    parameter is True, the complete event is printed to STDOUT.  This module should
    only be used for testing or demonstration purposes.    
    
    Parameters:
    
        - name (str):       The instance name when initiated.
        - complete (bool):  When True, print the complete event including headers.
        - purge (bool):     When True the message is dropped and not put in outbox.
        - counter (bool):   Puts an incremental number for each event in front of each event.
    
    Queues:
    
        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''
    
    def __init__(self, name, complete=False, purge=False, counter=False):
        PrimitiveActor.__init__(self, name)
        self.complete=complete
        self.purge=purge
        self.counter=counter
        self.c=0
        
    def consume(self,doc):
        
        if self.complete == False:
            print '%s - %s'%(self.c,doc['data'])
        else:
            print '%s - %s'%(self.c,doc['data'])
        if self.purge == False:
            self.putData(doc)
        self.c+=1
       
    def shutdown(self):
        self.logging.info('Shutdown')
