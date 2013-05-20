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
from gevent import spawn, sleep, signal, joinall
from gevent.event import Event
from mx.Stack import EmptyError

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
        self.__thread_consume=[]
        self.__thread_metrics=[]
        self.__thread_logs=[]
        self.__block=Event()
        self.__block.clear()
        self.__exit=Event()
        self.__exit.clear()

        self.__runConsumers=Event()
        self.__runConsumers.clear()

        self.__runMetrics=Event()
        self.__runMetrics.clear()

        self.__runLogs=Event()
        self.__runLogs.clear()

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
        '''

        self.logging.info('Stopping.')


        #Wait for all consumers
        self.__runConsumers.set()
        for thread in self.__thread_consume:
            thread.join()

        #Stop all modules
        self.__block.set()
        for module in self.__modules.keys():
            self.__modules[module].stop()

        #Stop all metric forwarders
        self.__runMetrics.set()
        for thread in self.__thread_metrics:
            thread.join()

        #Wait for all log forwarders
        self.__runLogs.set()
        for thread in self.__thread_logs:
            thread.kill()

        self.__exit.set()

    def register(self, module):
        '''Registers a Wishbone actor into the router.'''

        self.__modules[module.name]=module

        # Start to forward this module's logs to the registered
        # logging module.
        self.__thread_logs.append(spawn (self.__forwardLogging, module))

        # Start to forward this module's metrics to the registered
        # metrics module.
        self.__thread_metrics.append(spawn (self.__forwardMetrics, module))

    def connect(self, producer, consumer):
        '''Connects a producing queue to a consuming queue.'''

        self.__thread_consume.append(spawn (self.__consume, producer, consumer))

    def block(self):
        ''' A convenience function which blocks untill all registered
        modules are in a stopped state.

        Becomes unblocked when stop() is called and finisehd.
        '''

        self.__exit.wait()

    def __forwardLogging(self, module):

        '''A background greenlet which consumes the logs from a module and
        forwards them to the registered logging module.'''

        while not self.__runLogs.isSet():
            log = module.getLog()
            self.__logging.sendEvent(log, queue='inbox')

    def __forwardMetrics(self, module):

        '''A background greenlet which periodically gathers the metrics of all
        queues in all registered modules. These metrics are then forwarded to
        the registered metrics module.'''
        while not self.__runMetrics.isSet():
            metrics={"queue":{},"function":{}}
            if hasattr(module, "metrics"):
                for fn in module.metrics:
                    metrics["function"]["%s.%s"%(module.name, fn)]=module.metrics[fn]
            for queue in module.queuepool.listQueues():
                metrics["queue"]["%s.%s"%(module.name, queue)]=getattr(module.queuepool, queue).stats()
            print metrics
            sleep(self.interval)

    def __forwardRouterLogs(self):

        '''A background greenlet which forwards the logs created by this
        router to the registered logging module.'''

        while not self.__block.isSet():
            log = self.logging.logs.get()
            self.__logging.sendEvent(log,'inbox')

    def __consume(self, producer, consumer):

        '''The background greenthread which continuously consumes the producing
        queue and dumps that data into the consuming queue.'''

        (out_name, out_queue) = producer.split('.')
        (in_name, in_queue) = consumer.split('.')
        while not self.__runConsumers.isSet():
            try:
                (event, ticket) = self.__modules[out_name].getEvent(out_queue)
                try:
                    self.__modules[in_name].sendEvent(event, in_queue)
                    self.__modules[out_name].acknowledgeEvent(ticket)
                except:
                    self.__modules[out_name].cancelEvent(ticket)
            except EmptyError:
                self.__modules[out_name].waitUntilData(out_queue)
                pass

    def __signal_handler(self):

        '''Intercepts the SIGINT signal and initiates a proper shutdown
        sequence.'''

        self.logging.info("Received SIGINT. Shutting down.")
        self.stop()