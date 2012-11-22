#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       stdout.py
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


class STDOUT(PrimitiveActor):
    '''STDOUT class is a minimal Actor class which does nothing more than printing the messages from inbox and putting them back in outbox.
    
    Parameters:        

        * complete: If True, it prints out the message in Wishbone format including headers, if False only the content of the data field itself.
        * purge: When True the message is not put into the outbox but is purged.
    
    '''
    
    def __init__(self, name, complete=False, purge=False):
        PrimitiveActor.__init__(self, name)
        self.complete=complete
        self.purge=purge
        
    def consume(self,doc):
        if self.complete == False:
            print doc['data']
        else:
            print doc
        if self.purge == False:
            self.putData(doc)
       
    def shutdown(self):
        self.logging.info('Shutdown')
