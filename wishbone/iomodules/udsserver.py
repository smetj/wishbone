#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udsserver.py
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


class UDSServer(Greenlet, QueueFunctions, Block):
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

    Queues:

        - inbox:       Data coming from the outside world.
    '''

    def __init__(self, name, pool=True, path="/tmp"):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.pool=pool
        self.path=path
        self.logging = logging.getLogger( name )
        
        (self.sock, self.filename)=self.__setupSocket()
        
        self.logging.info("Initialiazed")

    def __setupSocket(self):
        if self.pool == True:
            if not path.exists(self.path):
                makedirs(self.path)
            filename = "%s/%s"%(self.path,uuid4())
            self.logging.info("Socket pool %s created."%filename)
        else:
            filename = self.path
            self.logging.info("Socket file %s created."%filename)
                
        sock=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind(filename)
        sock.listen(50)
        return (sock, filename)
    
    def handle(self, sock, address):
        sfile = sock.makefile()
        data=[]
        chunk = sfile.readlines()
        self.putData({'header':{},'data':''.join(chunk)}, queue='inbox')
        sfile.close()
        sock.close()
        
    def _run(self):
        try:
            StreamServer(self.sock, self.handle).serve_forever()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        remove(self.filename)
        self.logging.info('Shutdown')
