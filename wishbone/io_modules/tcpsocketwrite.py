#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcpsocketwrite.py
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

from wishbone.toolkit import PrimitiveActor
from gevent import socket,sleep
from random import randint
import logging


class TCPSocketWrite(PrimitiveActor):
    '''**A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.  
    
    If pool is True, path is expected to be a directory containing socket files over
    which the module will spread outgoing events.
    If pool if False, path is a socket file to which all outgoing events will be
    submitted.
        
    Parameters:

        - name (str):   The instance name when initiated.
        - pool (list):  A list of addresses:port entries to which data needs to be submitted.
        
    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
    '''

    def __init__(self, name, pool=True):
        PrimitiveActor.__init__(self, name)
        
        self.name=name
        self.pool=pool

        self.logging = logging.getLogger( name )
        self.logging.info('Initialiazed.')

        self.sockets=self.setupSockets()

    def setupSockets(self):
        pool=[]
        for entry in self.pool:
            (address,port)=entry.split(':')
            try:
                pool.append(socket.socket())
                pool[-1].connect( (address,int(port)) )
                self.logging.info("Connected to %s"%(pool[-1]))            
            except Exception as err:
                self.logging.warn("I could not connect to %s. Reason: %s"%(entry,err))            
        return pool
                
    def consume(self, doc):
        
        if isinstance(doc["data"],list):
            data = '\n'.join(doc["data"]) + '\n'
            
        while self.block()==True:
            try:
                destination = randint(0,len(self.sockets)-1)
                self.sockets[destination].sendall(data)
                break
            except Exception as err:
                self.logging.warn("Failed to write data to %s. Reason: %s"%(self.sockets[destination], err))
                sleep(1)
        
    def shutdown(self):
        self.logging.info('Shutdown')
