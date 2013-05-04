#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  default.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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

from wishbone.tools import QLogging
from gevent import spawn, sleep, signal
from gevent.event import Event

class Default():
    '''The default Wishbone router is responsible for shoveling the events
    from one queue to the other.

    It also intercepts ctrl+c in order to start a proper shutdown sequence.
    '''

    def __init__(self, logging=None, metrics=None):
        signal(2, self.signal_handler)
        self.logging=QLogging("Router")
        spawn (self.__forwardLocalLogs)
        self.__logging=logging
        self.__logging.start()
        self.__metrics=metrics
        self.__modules={}
        self.__running=[]
        self.__block=Event()
        self.__block.clear()

    def start(self):
        '''Starts the router by calling each registered module's start() function.'''

        self.__logging.start()
        self.logging.info('Starting.')
        for module in self.__modules.keys():
            self.__modules[module].start()

    def stop(self):
        '''Stops the router by calling each registered module's stop() function.

        When done makes the block() function unblocking.
        '''

        self.logging.info('Stopping.')
        for module in self.__modules.keys():
            self.__modules[module].stop()
        while not self.logging.logs.empty():
            sleep(0.5)
        self.__block.set()

    def register(self, module):
        '''Registers a Wishbone actor into the router'''

        self.__modules[module.name]=module
        spawn (self.__forwardLogging, module)

    def connect(self, producer, consumer):
        '''Connects a producing queue to a consuming queue.'''

        self.__running.append(spawn (self.__consume, producer, consumer))

    def block(self):
        '''Blocks until all registered modules are in stop state.

        When the stop() function finished it unblocks this block function.
        '''
        self.__block.wait()

    def __forwardLogging(self, module):
        '''A background greenlet which consumes the logs from a module and forwards them to the
        registered logging module.'''

        while True:
            log = module.getLog()
            self.__logging.sendEvent(log, queue='inbox')

    def __forwardLocalLogs(self):
        '''A background greenlet which forwards the logs created by this router.'''

        while True:
            self.__logging.sendEvent(self.logging.logs.get(),'inbox')

    def __consume(self, producer, consumer):
        '''The background greenlet which continuously consumes the producing queue and dumps that data into
        the consuming queue.'''

        (out_name, out_queue) = producer.split('.')
        (in_name, in_queue) = consumer.split('.')
        while True:
            self.__modules[in_name].sendEvent(self.__modules[out_name].getEvent(out_queue), in_queue)

    def signal_handler(self):
        '''Intercepts the SIGINT signal and initiates a proper shutdown sequence.'''

        self.logging.info("Received SIGINT. Shutting down.")
        self.stop()