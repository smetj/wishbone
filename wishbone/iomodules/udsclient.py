#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udsclient.py
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
from os import remove, path, makedirs, listdir
from itertools import cycle
import os
from gevent import Greenlet, sleep, socket
import stat
import logging


class UDSClient(PrimitiveActor):
    '''**A Wishbone IO module which writes data into a Unix domain socket.**

    Writes data into a Unix domain socket.  
    
    If pool is True, path is expected to be a directory containing socket files over
    which the module will spread outgoing events.
    If pool if False, path is a socket file to which all outgoing events will be
    submitted.
        
    Parameters:

        - name (str):   The instance name when initiated.
        - pool (bool):  When True expects path to be a pool of sockets.        
        - path (str):   The absolute path of the socket file or the socket pool.
        
    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events destined to the outside world.
    '''

    def __init__(self, name, pool=True, path="/tmp"):
        PrimitiveActor.__init__(self, name)
        
        self.name=name
        self.pool=pool
        self.path=path
        self.stream=stream
        self.reaptime=reaptime
        
        self.socketpool=[]
        self.logging = logging.getLogger( name )
        self.poolReaper()
        self.logging.info('Initialiazed.')

    def consume(self, doc):
        if isinstance(doc['data'],list):
            for data in doc["data"]:
                self.sendToSocket(data)
        else:
            self.sendToSocket(doc["data"])
    
    def sendToSocket(self, data):
        while self.block():
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                next_socket = self.socketcycle.next()
                sock.connect(next_socket)
                sock.sendall(data)
                self.logging.debug('Data send.')
                sock.close()
                break
            except Exception as err:
                self.logging.warn('Connecting failed. Will try again in a second. Reason: %s'%(err))
                self.poolReaper()
                sleep(1)

    def scheduleReaper(self):
        while self.block():
            self.poolReaper()
            sleep(self.reaptime)

    def poolReaper(self):
        '''Runs over the socket pool to build a list of available Unix Domain Sockets
        to choose from.'''

        socketlist=[]
        self.logging.info("Running poolReaper on %s"%self.path)
        for file in listdir(self.path):
            filename = "%s/%s"%(self.path,file)
            try:
                mode=os.stat(filename)
                if stat.S_ISSOCK(mode[0]) == True:
                    if os.access(filename,os.W_OK) == True:
                        socketlist.append(filename)
                    else:
                        self.logging.warn("%s is not writable."%filename)
                else:
                    self.logging.warn("%s is not a socket file."%filename)
            except Exception as err:
                self.logging.warn("There was a problem processing %s. Reason: %s"%(file,err))
        if self.socketpool != socketlist:
            self.socketpool = socketlist
            self.socketcycle = cycle(self.socketpool)

    def shutdown(self):
        self.logging.info('Shutdown')
