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
    '''The default Wishbone router.

    A router is responsible to:

        - Forward the events from one queue to the other.
        - Forward the logs from all modules to the logging module
        - Forward the metrics from all modules to the metrics module.

    SIGINT is intercepted and starts a proper shutdown sequence.

    '''

    def __init__(self, logging=None, metrics=None, interval=10):
        signal(2, self.__signal_handler)

        # Start the local logging instance
        ##################################
        self.logging=QLogging("Router")
        spawn (self.__forwardRouterLogs)

        # Start the logging module.
        ###########################
        self.__logging=logging
        self.__logging.start()

        # Start the metrics module.
        ###########################
        self.interval=interval
        # self.__metrics=metrics
        # self.__metrics=metrics.start()

        self.__modules={}
        self.__running=[]
        self.__block=Event()
        self.__block.clear()

    def start(self):
        '''Starts the router and all registerd modules.

        Executes following steps:

            - Starts the registered logging module.
            - Starts the registered metrics module.
            - Calls each registered module's start() function.
        '''

        self.__logging.start()
        self.logging.info('Starting.')
        for module in self.__modules.keys():
            self.__modules[module].start()

    def stop(self):
        '''Stops the router and all registered modules.


        Executes following steps:

            - Calls each registered module's stop() function.
            - Blocks untill the registered log module is empty.
            - Blocks untill the registered metrics module is empty.
            - When done makes the block() function unblocking.
        '''

        self.logging.info('Stopping.')
        for module in self.__modules.keys():
            self.__modules[module].stop()
        while not self.logging.logs.empty():
            sleep(0.5)
        self.__block.set()

    def register(self, module):
        '''Registers a Wishbone actor into the router.'''

        self.__modules[module.name]=module

        # Start to forward this module's logs to the registered
        # logging module.
        spawn (self.__forwardLogging, module)

        # Start to forward this module's metrics to the registered
        # metrics module.
        spawn (self.__forwardMetrics, module)

    def connect(self, producer, consumer):
        '''Connects a producing queue to a consuming queue.'''

        self.__running.append(spawn (self.__consume, producer, consumer))

    def block(self):
        ''' A convenience function which blocks untill all registered
        modules are in a stopped state.

        Becomes unblocked when stop() is called and finisehd.
        '''

        self.__block.wait()

    def __forwardLogging(self, module):

        '''A background greenlet which consumes the logs from a module and
        forwards them to the registered logging module.'''

        while not self.__block.isSet():
            log = module.getLog()
            self.__logging.sendEvent(log, queue='inbox')

    def __forwardMetrics(self, module):

        '''A background greenlet which periodically gathers the metrics of all
        queues in all registered modules. These metrics are then forwarded to
        the registered metrics module.'''
        while not self.__block.isSet():
            metrics={"queue":{},"function":{}}
            for module in self.__modules:
                if hasattr(self.__modules[module], "metrics"):
                    for fn in self.__modules[module].metrics:
                        metrics["function"]["%s.%s"%(module, fn)]=self.__modules[module].metrics[fn]
                for queue in self.__modules[module].queuepool.listQueues():
                        metrics["queue"]["%s.%s"%(module, queue)]=getattr(self.__modules[module].queuepool, queue).stats()
            print metrics
            sleep(self.interval)

    def __forwardRouterLogs(self):

        '''A background greenlet which forwards the logs created by this
        router to the registered logging module.'''

        while not self.__block.isSet():
            self.__logging.sendEvent(self.logging.logs.get(),'inbox')

    def __consume(self, producer, consumer):

        '''The background greenlet which continuously consumes the producing
        queue and dumps that data into the consuming queue.'''

        (out_name, out_queue) = producer.split('.')
        (in_name, in_queue) = consumer.split('.')
        while not self.__block.isSet():
            self.__modules[in_name].sendEvent(self.__modules[out_name].getEvent(out_queue), in_queue)

    def __signal_handler(self):

        '''Intercepts the SIGINT signal and initiates a proper shutdown
        sequence.'''

        self.logging.info("Received SIGINT. Shutting down.")
        self.stop()