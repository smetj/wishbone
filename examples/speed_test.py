#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  speed_test.py
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

#!/usr/bin/python

import wishbone
from wishbone.toolkit import PrimitiveActor
from wishbone.server import Server

class AddHeader(PrimitiveActor):
    def __init__(self, name, *args, **kwargs):
        PrimitiveActor.__init__(self, name)
    def consume(self,message):
        message['header']['broker_exchange'] = ''
        message['header']['broker_key'] = 'wb_speedtest'
        self.outbox.put(message)

class PassThrough(PrimitiveActor):
    def __init__(self, name, *args, **kwargs):
        PrimitiveActor.__init__(self, name)
    def consume(self,message):
        self.outbox.put(message)

def setup():

    wb = wishbone.Wishbone()
    wb.registerModule ( ('wishbone.io_modules', 'Broker', 'broker'), host='sandbox', vhost='/', username='guest', password='guest', consume_queue='wb_speedtest' )
    wb.registerModule ( ('__main__', 'AddHeader', 'addheader') )
    wb.registerModule ( ('__main__', 'PassThrough', 'pass1') )
    wb.registerModule ( ('__main__', 'PassThrough', 'pass2') )
    wb.connect (wb.broker.inbox, wb.addheader.inbox)
    wb.connect (wb.addheader.outbox, wb.pass1.inbox)
    wb.connect (wb.pass1.outbox, wb.broker.outbox)
    wb.start()

server = Server(instances=1, setup=setup)
server.start()

