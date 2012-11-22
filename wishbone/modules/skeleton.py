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


class Skeleton(PrimitiveActor):
    '''Skeleton class is a minimal Actor class which does nothing more than shoveling data from its inbox to its outbox.

    It can be used as an example/base for new blocks.
    
    Parameters:
    
        * name :    The name to assign to the module instance in Wishbone.
    '''
    
    def __init__(self, name):
        
        PrimitiveActor.__init__(self, name)
    
    def consume(self,doc):
        self.putData(doc)
       
    def shutdown(self):
        self.logging.info('Shutdown')
