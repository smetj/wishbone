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
from gevent.server import StreamServer
from wishbone.toolkit import QueueFunctions, Block


class SocketFile(Greenlet, QueueFunctions, Block):
    '''A Wishbone IO module which handles unix domain socket.    
    
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
        self.logging.info('Initialiazed.')

    def __setup(self):
        self.sock = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.sock.bind(self.name)
        
    def _run(self):
        try:
            StreamServer(bind_unix_listener('mysocket.sock'), handle).serve_forever()
        except KeyboardInterrupt:
            self.shutdown()
    
            

