#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       skeleton.py
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


class GotMessage(PrimitiveActor):
    '''A WishBone module which just logs whenever it gets a message and then discards.
    Also the length of the message is included in the log message.  It's not really useful.
    It's just made for testing purposes.
    '''
    
    def __init__(self, name, *args, **kwargs):
        PrimitiveActor.__init__(self, name)
    
    def consume(self,doc):
        self.logging.info('Got message with a size of %s characters.'%len(''.join(doc["data"])))
       
    def shutdown(self):
        self.logging.info('Shutdown')
