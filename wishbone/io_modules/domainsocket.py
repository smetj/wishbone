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

from os import remove, path, makedirs
from gevent.server import StreamServer
from gevent import Greenlet, socket, sleep
from gevent.queue import Queue
from wishbone.toolkit import QueueFunctions, Block
from uuid import uuid4
import logging


class DomainSocket(Greenlet, QueueFunctions, Block):
    '''**A Wishbone IO module which accepts external input from a unix domain socket.**

    Creates a Unix domain socket to which data can be submitted.

    The listener can run in 2 different modes:

        - blob: The incoming data is put into 1 event.
        - line: Each new line is treated as a new event.
    
    When pool is set to True, then path will considered to be directory.  If false,
    then path will be the filename of the socket file.

    Parameters:

        - name (str):           The instance name when initiated.
        - pool (bool):          When true path is considered to be a directory in 
                                which a socket with random name is created.
        - path (str):           The location of the directory or socket file.
        - mode (str):           The mode of the listener. [ "line","blob" ]

    Queues:

        - inbox:       Data coming from the outside world.
    '''

    def __init__(self, name, pool=True, path="/tmp", mode="line"):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.pool=pool
        self.path=path
        self.mode = mode
        self.logging = logging.getLogger( name )
        
        self.filename=self.__setupSocket()
        
        if self.mode == "line":
            self.handle=self.__doLine
        elif self.mode == "blob":
            self.handle=self.__doBlob            
        self.logging.info('Initialiazed in %s mode.'%self.mode)

    def __setupSocket(self):
        if self.pool == True:
            if not path.exists(self.path):
                makedirs(self.path)
            filename = "%s/%s"%(self.path,uuid4())
            self.logging.info("Socket pool %s created."%filename)
        else:
            filename = self.path
            self.logging.info("Socket file %s created."%filename)
                
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.sock.bind(filename)
        self.sock.listen(50)
        return filename
    
    def __doBlob(self, socket, address):
        '''All incoming data is treated as 1 event.'''

        fileobj = socket.makefile()
        data = fileobj.readlines()
        self.logging.debug ('Data received from %s' % (address) )
        self.putData({'header':{},'data':''.join(data)}, queue='inbox')
        fileobj.close()

    def __doLine(self, socket, address):
        '''Treats every newline as a new event.'''

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

    def _run(self):
        try:
            StreamServer(self.sock, self.handle).serve_forever()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        remove(self.filename)
        self.logging.info('Shutdown')
