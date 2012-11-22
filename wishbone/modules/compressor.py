#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       compressor.py
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
import snappy
import json

class Compressor(PrimitiveActor):
    '''A Wishbone module which compresses uncompressed data and decompresses compressed data using Snappy.
    
    The module detects whether data is compressed or not.
    '''
    
    def __init__(self, name):
        PrimitiveActor.__init__(self, name)
      
    def consume(self,message):
        data = json.dumps(message['data'])
        if snappy.isValidCompressed(data):
            self.logging.debug('Data decompressed.')
            self.putData(snappy.decompress(data))
        else:
            self.logging.debug('Data compressed.')
            message['data'] = snappy.compress(data)
            message['header']['compression']='snappy'
            self.putData(message)
