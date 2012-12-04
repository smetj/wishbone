#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       snappy.py
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

class Snappy(PrimitiveActor):
    '''**A Wishbone module which compresses or decompresses data using Snappy.**

    This module can be initiated in 2 modes:
        - compress
        - decompress

    When initiated in "compress" mode it will compress all incoming data.  When
    initiated in "decompress" mode, it will try to decompress all incoming data.

    When purges is set to True, incoming events will be dropped when decompression
    fails, otherwise it will be forwarded in its original state.
    
    Watch out, compression is cpu bound, which could impact your event loop.

    Parameters:

        - name (str):       The instance name when initiated.
        - mode (str):       "compress" or "decompress"
        - purge (bool):     When true then the event will be purged if decompression fails.
        
    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    def __init__(self, name, mode="compress", purge=True):
        PrimitiveActor.__init__(self, name)
        self.name=name
        self.mode=mode
        self.purge=purge
        if mode == "compress":
            self.consume = self.__compress
        elif mode == "decompress":
            self.consume = self.__decompress

    def __compress(self,message):
        message['data']=snappy.compress(message['data'])
        message['header']['snappy']=True
        self.logging.debug("Incoming data compressed.")
        self.putData(message)

    def __decompress(self,message):
        try:
            message['data']=snappy.decompress(message['data'])
            self.logging.debug("Incoming data decompressed.")
            message['header']['snappy']=False
            self.putData(message)
        except Exception as err:
            self.logging.warn("Decompressing failed. Reason: %s"%err)
            if self.purge != True:
                self.putData(message)
