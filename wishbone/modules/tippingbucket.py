#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       tippingbucket.py
#
#       Copyright 2012 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone.toolkit import PrimitiveActor
from time import time
from gevent import sleep, spawn
from gevent.event import Event
from gevent import monkey;monkey.patch_all()

class TippingBucket(PrimitiveActor):
    
    '''Buffers unicode data and dumps to the output on 2 conditions:

        * Last data enteered in buffer is older than x seconds.
        * Total data in buffer is x size.

    When the buffer is empty, the header of the first incoming message will be used as the header
    for the message going out containing the content of the buffer.  If you want to override that
    header with a predefined one then use the <predefined_header> option.
    
    Realize this is a buffer PER WishBone instance.

    Parameters:

        * age:  The time in seconds since the first update when the buffer is flushed.
                Default: 10
                Type: Int

        * size: The total size in bytes of the buffer when it is flushed.
                Default: 10000
                Type: Int
        
        * predefined_header:    Once the buffer is flushed the message containing the content of the
                                buffer will have this header instead of the header coming from the
                                first package entering the buffer.
    
    Disclaimer: The size of the buffer is expressed in bytes.  This is *only* valid when you use
                "single-byte encoding" characters.  Even then it's going to be an approximation.
                When unicode is used then this counter is not going to be realistic anymore.
                
    Disclaimer2:    Binary data is not going to work.  If you require that, encode into base64 or
                    something similar.  In that case take the growth of that into account:
                    
                        ~ output_size = ((input_size - 1) / 3) * 4 + 4
                    
                    So 256 bytes binary data results into 344 bytes of Base64 data.
    
    ToDo(smetj):    Check for each incoming string which type of encoding we're talking about
                    and take into account when "calculating" the total size of the buffer.
                
    '''

    def __init__(self, name, age=5, size=10000, predefined_header=None):

        PrimitiveActor.__init__(self, name)
        self.age = age
        self.size = size
        self.predefined_header=predefined_header
        self.buff=[]
        self.buff_age=0
        self.buff_size=0
        self.buff_header={}
        spawn(self.reaper)

    def consume(self,doc):

        if self.buff_age==0:
            self.buff_age=time()
            self.header=doc["header"]

        self.buff.append(doc["data"])
        self.buff_size+=len((doc["data"]))

        if self.buff_size > self.size:
            self.logging.info("Size of buffer exceeded. Flushed.")
            self.flushBuffer()

    def reaper(self):
        '''Check whether our cache is expired and flush the buffer if its the case.'''

        while self.block():
            if self.buff_age != 0:
                if (float(time()) - float(self.buff_age)) > float(self.age):
                    self.flushBuffer()
                    self.logging.info("Age of buffer exceeded %s seconds. Flushed."%(self.age))
            sleep(0.1)

    def flushBuffer(self):
        '''Flushes the buffer.'''

        if self.predefined_header == None:
            self.putData({"header":self.buff_header, "data":self.buff})
        else:
            self.putData({"header":self.predefined_header, "data":self.buff})
        self.resetBuffer()
        sleep(0)

    def resetBuffer(self):
        '''Resets the counters.'''
        
        self.buff=[]
        self.buff_age=0
        self.buff_size=0
        self.buff_header={}

    def shutdown(self):
        self.logging.info('Shutdown')
