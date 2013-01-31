#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mongotools.py
#  
#  Copyright 2013 Jelle Smet development@smetj.net
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
from pymongo import Connection
from gevent import Greenlet
from gevent import monkey; monkey.patch_all()
      

class MongoTools():
    '''A baseclass which offers MongoDB connectivity and functionality.'''
    
    def setupConnection(self):
        '''Wrapper for calling __setupConnection.  Spawned into a greenlet so it doesn't block us.'''
        self.connected=False
        Greenlet.spawn(self.__setupConnection)
    
    def __setupConnection(self):
        '''Is called by setupConnection, tries to connect until succeeds or block is lifted.'''
        
        while self.block() == True:
            try:
                self.conn = Connection( self.host, self.port, use_greenlets=True )
            except:
                self.logging.error('I could not connect to the MongoDB database.  Will try again in 1 second')
                self.wait(timeout=1)    
            else:
                self.logging.info('Connected')
                self.connected=True
                break
                
            
        
