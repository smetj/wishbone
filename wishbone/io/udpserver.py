#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  io.py
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
import logging


class UDPServer(DatagramServer):
 
    def __init__(self, port, *args, **kwargs):
        DatagramServer.__init__(self, ':'+port, *args, **kwargs)
        self.logging = logging.getLogger( 'UDPServer' )
        self.logging.info ( 'started and listening on port %s' % port)
        self.inbox=Queue(None)        
        spawn(self.run)
 
    def handle(self, data, address):
        self.logging.info ('%s: Data received.' % (address[0]) )
        self.inbox.put(data)
 
    def run(self):
        self.serve_forever()
