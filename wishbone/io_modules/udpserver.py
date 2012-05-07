#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udpserver.py
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

from gevent import spawn
from gevent.queue import Queue
from gevent.server import DatagramServer
from wishbone.toolkit import QueueFunctions
import logging


class UDPServer(DatagramServer, QueueFunctions):
    '''A Wishbone module which handles UDP input.
    
    Data received by the module is put into self.inbox
    
    Parameters:
        name:       The name you want this module to be registered under.
        port:       The port on which the server should listen.
    '''
 
    def __init__(self, name, port, *args, **kwargs):
        DatagramServer.__init__(self, ':'+port, *args, **kwargs)
        QueueFunctions.__init__(self)
        self.logging = logging.getLogger( name )
        self.name = 'UDPServer'
        self.logging.info ( 'started and listening on port %s' % port)
        self.inbox=Queue(None)
        spawn(self.run)
 
    def handle(self, data, address):
        '''Is called upon each incoming message, makes sure the data has the right Wishbone format and writes the it into self.inbox'''
        
        self.logging.debug ('Data received from %s' % (address[0]) )
        self.sendData({'header':{},'data':data}, queue='inbox')
 
    def run(self):
        '''Blocking function which starts the UDP server.'''
        
        self.serve_forever()

    def shutdown(self):
        '''This function is called on shutdown().'''
        self.lock=False
        self.logging.info('Shutdown')
