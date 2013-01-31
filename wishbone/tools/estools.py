#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  estools.py
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
import pyes
from gevent import Greenlet
from gevent import monkey; monkey.patch_all()
       
class ESTools():
    '''A baseclass which offers ElasticSearch connectivity and functionality.'''
    
    def es_index(self, *args, **kwargs):
        '''Wrapper around ES.index()
        
        When ES is not available it tries to resubmit the document untill the general block is cancelled.'''
    
        while self.block() == True:
                while self.connected == False:
                    self.wait(0.5)                

                try:
                    id = self.conn.index(*args, **kwargs)
                    
                except Exception as err:
                    self.setupConnection()
                
                else:
                    break
        return id
    
    def setupConnection(self):
        '''Wrapper for calling __setupConnection.  Spawned into a greenlet so it doesn't block us.'''
        
        self.connected=False
        Greenlet.spawn(self.__setupConnection)
       
    def __setupConnection(self):
        '''Is called by setupConnection, tries to connect until succeeds or block is lifted.'''
        
        while self.block() == True:
            try:
                self.conn =  pyes.ES([self.host])
                if self.conn.collect_info() == False:
                    raise Exception ('Unable to connect.')
            except Exception as err:   
                self.logging.error('Could not connect to ElasticSearch. Waiting for a second.  Reason: %s' %(err))
                self.wait(timeout=1)
            else:
                self.logging.info('Connected')
                self.connected=True
                break
