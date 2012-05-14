#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  server.py
#  
#  Copyright 2012 Jelle Smet development@smetj.net
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
from multiprocessing import Process, Event
from time import sleep


class Server():
    '''Handles starting, stopping and daemonizing of one or multiple Wishbone instances.''' 
    
    def __init__(self, instances=1, setup=None, log_level=logging.INFO):
        self.instance=instances
        self.setup=setup
        self.log_level=log_level
        self.wishbone=None
        self.processes=[]
        self.configureLogging()
        self.logging = logging.getLogger( 'Server' )
    
    def start(self):
        '''Starts the environment.'''
        
        for number in range(self.instance):
            self.processes.append(Process(target=self.setup, name=number))
            self.processes[number].start()
            self.logging.info('Instance #%s started.'%number)
        
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        '''Stops the environment.'''
        
        self.logging.info('SIGINT received. Stopping')
        for process in self.processes():
            self.logging.info('Waiting for %s' %self.processes[process].name)
            process.join()
        logging.shutdown()
            
    def configureLogging(self,syslog=False,loglevel=logging.INFO):
        '''Configures logging.
        
        Configures the format of the logging messages.  This function accepts 1 parameter:
        
        loglevel: defines the loglevel.'''
        
        format=('%(asctime)s %(levelname)s %(name)s: %(message)s')
        if syslog == False:
            logging.basicConfig(level=loglevel, format=format)
        else:
            logger = logging.getLogger()
            logger.setLevel(loglevel)
            syslog = SysLogHandler(address='/dev/log')
            formatter = logging.Formatter(format)
            syslog.setFormatter(formatter)
            logger.addHandler(syslog)

