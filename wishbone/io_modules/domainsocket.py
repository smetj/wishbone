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
from os import remove
from gevent.server import StreamServer
from gevent import Greenlet, socket, sleep
from gevent.queue import Queue
from wishbone.toolkit import QueueFunctions, Block


class DomainSocket(Greenlet, QueueFunctions, Block):
    '''**A Wishbone IO module which accepts external input from a unix domain socket.**
    
    Creates a Unix domain socket to which data can be submitted.
    The listener can run in 2 modes:
    
    - line: Each newline creates a Wishbone event.
    - blob: Data comes in as 1 event untill client disconnects.
        
    Parameters:

        - name (str):   The instance name when initiated.
        - path (str):   The absolute path of the socket.
        - mode (str):   The mode UDP listener is in.  [ line, blob ]
    
    Queues:
    
        - inbox:       Data coming from the outside world.        
    ''' 
   
    def __init__(self, name, path, mode="line"):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.logging = logging.getLogger( name )
        self.path = path
        self.mode = mode
        self.sock = None
        self.__setup()
        self.logging.info('Initialiazed in %s mode'%self.mode)

    def __setup(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.sock.bind(self.path)
        self.sock.listen(50)
        if self.mode == "line":
            self.handle=self.__doLine
        elif self.mode == "blob":
            self.handle=self.__doBlob    
    
    def __doLine(self, socket, address):
        '''Is called upon each incoming message, makes sure the data has the right Wishbone format and writes the it into self.inbox'''
        
        fileobj = socket.makefile()
        while self.block():
            line = fileobj.readline()
            if not line:
                self.logging.debug('Client disconnected.')
                break
            else:
                self.logging.debug ('Data received from %s' % (address) )     
                self.putData({'header':{},'data':line.rstrip("\n")}, queue='inbox')
            sleep(0)
        fileobj.close()
    
    def __doBlob(self, socket, address):
        '''Is called upon each incoming message, makes sure the data has the right Wishbone format and writes the it into self.inbox'''
        
        fileobj = socket.makefile()
        blob = fileobj.readlines()
        fileobj.close()
        self.logging.debug ('Data received from %s' % (address) )     
        self.putData({'header':{},'data':"".join(blob)}, queue='inbox')        
         
    def _run(self):
        try:
            StreamServer(self.sock, self.handle).serve_forever()
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        remove(self.path)
        self.logging.info('Shutdown')
