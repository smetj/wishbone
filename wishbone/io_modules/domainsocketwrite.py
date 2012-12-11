#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  domainsocketwrite.py
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


class DomainSocketWrite(Greenlet, QueueFunctions, Block):
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

    def __init__(self, name, path=None):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.path=path
        self.logging = logging.getLogger( name )
        self.logging.info('Initialiazed. in %s mode.'%self.mode)

    def handle(self, doc):
        pass
        
    def _run(self):
        #read socket        

    def getStatusSockets(self):
        pass

    def shutdown(self):
        self.logging.info('Shutdown')
