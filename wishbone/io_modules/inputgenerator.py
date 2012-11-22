#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       inputgenerator.py
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
from string import ascii_uppercase, ascii_lowercase, digits
from random import choice, uniform, randint
from wishbone.toolkit import QueueFunctions, Block
from gevent import Greenlet, spawn, sleep, spawn_later
from gevent.event import Event
from gevent.queue import Queue
from time import time, strftime, localtime
from gevent import monkey;monkey.patch_all() 

class InputGenerator(Greenlet, QueueFunctions, Block):
    '''

    A WishBone class which generates random data at different configurable specifications.
    It's primary use is for testing.

    Parameters:
    
        * min_payload:  The minimum length of each random generated message.
                        Default: 0
                        Type: Integer

        * max_payload:  The maximum length of each random generated message.
                        Default: 1
                        Type: Integer

        * min_interval: The minimum time in seconds between each generated messages.
                        Default: 0
                        Type: Integer

        * max_interval: The maximum time in seconds between each generated messages.
                        Default: 0
                        Type: Integer

        * min_outage_start: The minimum time in seconds the next outage can start.
                            Default: 60
                            type: Int

        * max_outage_start: The maximum time in seconds the next outage can start.
                            Default: 600
                            type: Int
        
        * min_outage_length:    The minimum time in seconds an outage can last.
                                Default: 0
                                Type: Integer
                        
        * max_outage_length:    The maximum time in seconds an outage can last.
                                Default: 0
                                Type: Integer
        
        length:     Simulates the variable length of message data.
        
        interval:   Simulates the variable interval rate data is produced.
        
        outage:     Simulates the connectivity problems for incoming data.  Under normal conditions
                    there's a constant stream.  It might happen however incoming connection is
                    interrupted, data is being build up somewhere and after connectivity restores a
                    big chunk of data comes in.
    '''

    def __init__(self, name, min_payload=0,max_payload=1,min_interval=0,max_interval=0,min_outage_start=60,max_outage_start=600,min_outage_length=0,max_outage_length=0):

        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        
        self.logging = logging.getLogger( name )
        self.logging.info ( 'Initiated' )
                
        self.name = name
        self.min_payload=min_payload
        self.max_payload=max_payload
        self.min_interval=min_interval
        self.max_interval=max_interval
        self.min_outage_start=min_outage_start
        self.max_outage_start=max_outage_start
        self.min_outage_length=min_outage_length
        self.max_outage_length=max_outage_length
        
        self.createQueue("temp")
        self.outage=Event()
        spawn(self.reaper)

    def decode (self, gearman_worker, gearman_job):
        self.logging.debug ('Data received.')

    def _run(self):
        self.logging.info('Started')
        while self.block():
            
            random_string = ''.join(choice(ascii_uppercase + ascii_lowercase + digits) for x in range(self.min_payload)+range(randint(0, self.max_payload)))
            self.logging.debug('Data batch generated with size of %s bytes.'%len(random_string))
            self.putData({"header":{},"data":random_string},"temp")
            
            sleeping_time = uniform(self.min_interval,self.max_interval)
            self.logging.debug('Waiting for %s seconds until the next data batch is generated.'%sleeping_time)
            sleep(sleeping_time)            

    def reaper(self):
        
        '''The reaper runs actually submits the randomly generated data from the local queue into the outgoing queue.
        The goal of this is to make to reaper stop working for min_outage to max_outage to simulate an outage.
        '''
        
        self.planOutage()
        while self.block():
            self.outage.wait()
            self.sendData(self.getData("temp"),queue='inbox')
            
    def planOutage(self):
        '''Plans when the next outage will occur.'''
        
        start_outage=uniform(self.min_outage_start, self.max_outage_start)
        spawn_later(start_outage,self.executeOutage)
        self.logging.info('Next outage is planned at %s'%(strftime("%a, %d %b %Y %H:%M:%S +0000", localtime(time()+start_outage))))
    
    def executeOutage(self):
        '''Executes the outage by locking the reaper.'''
        
        self.outage.clear()
        outage_length=uniform(self.min_outage_length, self.max_outage_length)
        self.logging.info("Outage of %s seconds started."%(outage_length))
        sleep(outage_length)
        self.logging.info("Outage finished.")
        self.planOutage()
        self.outage.set()
        
    def shutdown(self):
        self.logging.info('Shutdown')
