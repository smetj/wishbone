#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wishbone.py
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

import logging
import io
from importlib import import_module
from gevent import Greenlet, sleep, spawn
from gevent.queue import Queue


class Wishbone():
    
    def __init__(self):
        self.lock=True
        self.__configureLogging()
        
    def registerModule(self, module_name, class_name, name, *args, **kwargs):
        try:
            loaded_module = import_module(module_name)
            setattr(self, name, getattr (loaded_module, class_name)(name, self.block, *args, **kwargs))
        except Exception as err:
            print "Problem loading module: %s and class %s. Reason: %s" % ( module_name, class_name, err)

    def registerBroker(self, *args, **kwargs):
        self.broker = io.Broker(block=self.block, *args, **kwargs )
    
    def registerUDPServer(self, port='9000', *args, **kwargs):
        self.udp_server = io.UDPServer(port, *args, **kwargs)
    
    def connect(self,inbox,outbox):
        spawn ( self.__connector, inbox, outbox )
    
    def start(self):
        for instance in self.__dict__:
            try:
                self.__dict__[instance].start()
            except:
                pass
        while self.block() == True:
            sleep(0.01)

    def stop(self):
        self.lock=False
        for instance in self.__dict__:
            try:
                self.__dict__[instance].shutdown()
            except:
                pass
    
    def block(self):
        return self.lock
         
    def __connector(self,inbox, outbox):
        '''Consumes data from inbox and puts it in outbox.'''
        while self.block() == True:
                outbox.put(inbox.get())
        
    def __configureLogging(self,syslog=False,loglevel=logging.INFO):
        format=('%(asctime)s %(levelname)s %(name)s %(message)s')
        if syslog == False:
            logging.basicConfig(level=loglevel, format=format)
        else:
            logger = logging.getLogger()
            logger.setLevel(loglevel)
            syslog = SysLogHandler(address='/dev/log')
            formatter = logging.Formatter(format)
            syslog.setFormatter(formatter)
            logger.addHandler(syslog)

class PrimitiveActor(Greenlet):

    def __init__(self, name, block):
        Greenlet.__init__(self)
        self.logging = logging.getLogger( name )
        self.logging.info('Initiated.')
        self.block = block
        self.inbox = Queue(None)
        self.outbox = Queue(None)
        
    def _run(self):
        self.logging.info('Started.')
        while self.block() == True:
            message = self.inbox.get()
            self.consume(message)
