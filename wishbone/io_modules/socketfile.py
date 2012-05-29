#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  socket_file.py
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
import _socket
import os
from gevent.server import StreamServer
from gevent import Greenlet
from gevent.queue import Queue
from wishbone.toolkit import QueueFunctions, Block


class SocketFile(Greenlet, QueueFunctions, Block):
    '''A Wishbone IO module which handles unix domain socket input.    
    
    Parameters:

        * name:       The name you want this module to be registered under.
        * file:       The absolute filename of the named pipe.
    ''' 
   
    def __init__(self, name, *args, **kwargs):
        Greenlet.__init__(self)
        Block.__init__(self)
        self.name=name
        self.logging = logging.getLogger( name )
        self.file = kwargs.get('file', 'wishboneInput.socket')
        self.inbox=Queue(None)
        self.sock = self.__setup()
        self.logging.info('Initialiazed.')

    def __setup(self):
        sock = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
        sock.setblocking(0)
        sock.bind(self.file)
        sock.listen(50)
        return sock

    def handle(self, socket, address):
        '''Is called upon each incoming message, makes sure the data has the right Wishbone format and writes the it into self.inbox'''
        
        fileobj = socket.makefile()
        while True:
            line = fileobj.readline()
            if not line:
                self.logging.debug('Client disconnected.')
                break
            else:
                self.sendData({'header':{},'data':line.rstrip("\n")}, queue='inbox')

        #self.logging.info ('Data received from %s' % (address) )        
        fileobj.close()
        
    def _run(self):
        try:
            StreamServer(self.sock, self.handle).start()
            self.wait()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        os.remove(self.file)
        self.logging.info('Shutdown')
            

