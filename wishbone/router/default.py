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
from wishbone.tools import WishboneQueue
from collections import deque
from gevent import spawn, sleep, signal, joinall, kill
from gevent.event import Event

class Default():
    '''The default Wishbone router.

    A router is responsible to:

        - Forward the events from one queue to the other.
        - Forward the logs from all modules to the logging module
        - Forward the metrics from all modules to the metrics module.

    SIGINT is intercepted and initiates a proper shutdown sequence.

    Parameters:

        - interval(int):    The interval metrics are polled from each module
        - rescue(bool):     Whether to extract any events stuck in one of
                            the queues and write that to a cache file.  Next
                            startup the events are read from the cache and
                            inserted into the same queue again.

    '''

    def __init__(self, interval=10, rescue=False):
        self.interval=interval
        self.rescue=rescue

        signal(2, self.__signal_handler)
        self.logging=QLogging("Router")
        self.logs=WishboneQueue()
        self.metrics=WishboneQueue()

        # Forward router's logs to logging queue.
        #########################################
        spawn (self.__forwardEvents, self.logging.logs, self.logs)

        self.__modules=[]
        self.__fwd_metrics=[]
        self.__fwd_logs=[]
        self.__fwd_events=[]

        self.__block=Event()
        self.__block.clear()
        self.__exit=Event()
        self.__exit.clear()

        self.__runConsumers=Event()
        self.__runConsumers.clear()

        self.__runLogs=Event()
        self.__runLogs.clear()

    def block(self):
        ''' A convenience function which blocks untill all registered
        modules are in a stopped state.

        Becomes unblocked when stop() is called and finisehd.
        '''

        self.__exit.wait()

    def connect(self, producer, consumer):
        '''Connects a producing queue to a consuming queue.'''

        if isinstance(producer._WishboneQueue__q, deque) and isinstance(consumer._WishboneQueue__q, deque):
            self.__fwd_events.append(spawn (self.__forwardEvents, producer, consumer))
        else:
            raise Exception("Not a WishboneQueue.")

    def doRescue(self):
        '''Runs over each queue to extract any left behind messages.
        '''

        for module in reversed(self.__modules):
            for queue in module.queuepool.messagesLeft():
                for blah in module.queuepool.dump(queue):
                    print blah

    def register(self, module):
        '''Registers a Wishbone actor into the router.'''

        self.__modules.append(module)

        # Start to forward this module's logs to the registered
        # logging module.
        self.__fwd_logs.append(spawn (self.__forwardLogs, module.logging.logs, self.logs))

        # Start to forward this module's metrics to the registered
        # metrics module.
        self.__fwd_metrics.append(spawn (self.__forwardMetrics, module))

    def start(self):
        '''Starts the router and all registerd modules.

        Executes following steps:

            - Starts the registered logging module.
            - Starts the registered metrics module.
            - Calls each registered module's start() function.
        '''

        self.logging.info('Starting.')
        for module in self.__modules:
            module.start()

    def stop(self):
        '''Stops the router and all registered modules.

        The modules are stopped in the reverse order they were registered. The
        first module registered is never actually stopped.  The reason for
        this is to register the logging module first, to be able to handle
        logs untill the end.

        This approch is subject to change, but for the time being this is it.
        '''

        self.logging.info('Stopping.')


        #Stops all modules (except the 1st one registered) in reverse order
        for module in reversed(self.__modules[1:]):
            module.stop()
            for thread in module._Consumer__greenlet:
                thread.join(1)
                thread.kill()

        self.__runConsumers.set()
        for thread in self.__fwd_events:
            try:
                thread.join(0.5)
            except:
                thread.kill()

        for thread in self.__fwd_metrics:
            try:
                thread.join(0.5)
            except:
                thread.kill()

        if self.rescue:
            self.doRescue()

        self.__exit.set()

    def __forwardMetrics(self, module):

        '''A background greenlet which periodically gathers the metrics of all
        queues in all registered modules. These metrics are then forwarded to
        the registered metrics module.'''

        while not self.__runConsumers.isSet():
            metrics={"queue":{},"function":{}}
            if hasattr(module, "metrics"):
                for fn in module.metrics:
                    metrics["function"]["%s.%s"%(module.name, fn)]=module.metrics[fn]
            for queue in module.queuepool.listQueues():
                metrics["queue"]["%s.%s"%(module.name, queue)]=getattr(module.queuepool, queue).stats()
            self.metrics.put({"header":{},"data":metrics})
            sleep(self.interval)

    def __forwardEvents(self, producer, consumer):

        '''The background greenthread which continuously consumes the producing
        queue and dumps that data into the consuming queue.'''

        while not self.__runConsumers.isSet():
            try:
                data = producer.get()
            except:
                sleep(0.1)
            else:
                if self.__checkIntegrity(data):
                    try:
                        consumer.put(data)
                    except:
                        producer.rescue(data)
                else:
                    self.logging.warn("Invalid event format.")
                    self.logging.debug("Invalid event format. %s"%(data))

    def __forwardLogs(self, producer, consumer):

        '''The background greenthread which continuously consumes the producing
        queue and dumps that data into the consuming queue.'''

        while not self.__runLogs.isSet():
            try:
                data = producer.get()
            except:
                sleep(0.1)
            else:
                if self.__checkIntegrity(data):
                    try:
                        consumer.put(data)
                    except:
                        producer.rescue(data)
                else:
                    self.logging.warn("Invalid event format.")
                    self.logging.debug("Invalid event format. %s"%(data))

    def __signal_handler(self):

        '''Intercepts the SIGINT signal and initiates a proper shutdown
        sequence.'''

        self.logging.info("Received SIGINT. Shutting down.")
        self.stop()

    def __checkIntegrity(self, event):
        '''Checks the integrity of the messages passed over the different queues.

        The format of the messages should be

        { 'headers': {}, data: {} }
        '''

        if type(event) is dict:
            if len(event.keys()) == 2:
                if event.has_key('header') and event.has_key('data'):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False