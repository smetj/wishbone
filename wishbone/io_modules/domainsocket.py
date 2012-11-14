#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  domainsocket.py
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
#import _socket
from os import remove
from gevent.server import StreamServer
from gevent import Greenlet, socket, sleep
from gevent.queue import Queue
from wishbone.toolkit import QueueFunctions, Block


class DomainSocket(Greenlet, QueueFunctions, Block):
    '''A Wishbone IO module which handles unix domain socket input.    
    
    Parameters:

        * name:       The name you want this module to be registered under.
        * file:       The absolute filename of the socket.
    ''' 
   
    def __init__(self, name, *args, **kwargs):
        Greenlet.__init__(self)
        Block.__init__(self)
        self.name=name
        self.logging = logging.getLogger( name )
        self.file = kwargs.get('file', '%s.socket'%self.name)
        self.sock = None
        self.__setup()
        self.inbox=Queue()
        self.logging.info('Initialiazed.')

    def __setup(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.sock.bind(self.file)
        self.sock.listen(50)
        
    
    def handle(self, socket, address):
        '''Is called upon each incoming message, makes sure the data has the right Wishbone format and writes the it into self.inbox'''
        
        fileobj = socket.makefile()
        while self.block():
            line = fileobj.readline()
            if not line:
                self.logging.debug('Client disconnected.')
                break
            else:
                self.logging.debug ('Data received from %s' % (address) )     
                self.sendData({'header':{},'data':line.rstrip("\n")}, queue='inbox')
            sleep(0)
        fileobj.close()
        
        
    def _run(self):
        try:
            StreamServer(self.sock, self.handle).serve_forever()
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        remove(self.file)
        self.logging.info('Shutdown')
