#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udp_server.py
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

from wishbone.wishbone import Wishbone
from wishbone.server import Server


if __name__ == '__main__':    
    def setup():    
        wb = Wishbone()
        wb.registerModule ( ('wishbone.io_modules', 'NamedPipe', 'named_pipe'), file='/tmp/named_pipe_server' )
        wb.registerModule ( ('wishbone.modules', 'STDOUT', 'stdout'), complete=True, purge=True )
        wb.connect (wb.named_pipe.inbox, wb.stdout.inbox)        
        wb.start()
        
    server = Server(instances=1, setup=setup, daemonize=False, name='named_pipe_server')
    server.start()
