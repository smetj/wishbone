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
import ast

class TippingBucket(PrimitiveActor):
    '''Buffers data and dumps to the output on 2 conditions:
        
        * Last data enteered in buffer is older than x seconds.
        * Total data in buffer is x size.
    
    The messages with the same header are buffered together.        
    Realize this is a buffer PER WishBone instance.

    Parameters:
    
        * age:  The time in seconds since the first update when the buffer is flushed.
                Default: 10
                Type: Int
                
        * size: The total size of the buffer when it is flushed.
                Default: 10000
                Type: Int
    '''
    
    def __init__(self, name, *args, **kwargs):
        
        PrimitiveActor.__init__(self, name)
        self.age = kwargs.get('age',5)
        self.size = kwargs.get('size',10000)
        self.buff={}
        spawn(self.reaper)
        
    def consume(self,doc):
        key = str(doc["header"])

        if not key in self.buff:
            self.buff[key]={"length":0,"last":0,"data":[]}
            self.buff[key]["last"]=time()            
        
        self.buff[key]["data"].append(doc["data"])
        self.buff[key]["length"]+=len(str(doc["data"]))
        
        if self.buff[key]["length"] > self.size:
            self.logging.info("Size of buffer %s exceeded %s. Flushed."%(key,self.size))
            self.dumpPart(key)
    
    def reaper(self):
        '''Run over the dictionary every x seconds to see whether we have expired cache which needs to be dumped.'''
        
        while self.block():
            items=[]
            for item in self.buff:
                if (float(time()) - float(self.buff[item]["last"])) > float(self.age):
                    self.logging.info("Age of buffer %s exceeded %s seconds. Flushed."%(item,self.age))
                    items.append(item)
            
            for item in items:
                self.dumpPart(item)
            sleep(0.1)
            
    def dumpPart(self, key):
        '''Dumps the expired cache into the queue and deletes the key from the cache dictonary.'''
        
        header = ast.literal_eval(key)
        self.sendData({"header":header,"data":self.buff[key]["data"]})
        del(self.buff[key])
    
    def shutdown(self):
        self.logging.info('Shutdown')
