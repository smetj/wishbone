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
from wishbone.errors import QueueMissing
from collections import deque
from gevent import spawn, sleep, signal, joinall, kill
from gevent.event import Event
from gevent import Greenlet
from collections import OrderedDict

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

        #self.__modules = OrderedDict()
        self.__modules = {}
        self.__logmodule = None
        self.__metricmodule = None

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

        (producer_module, producer_queue) = producer.split(".")
        (consumer_module, consumer_queue) = consumer.split(".")

        while True:
            try:
                producer_queue_instance = getattr(self.__modules[producer_module]["instance"].queuepool, producer_queue)
                break
            except:
                self.logging.info("Queue %s does not exist in module %s.  Autocreate queue."%(producer_queue, producer_module))

        while True:
            try:
                consumer_queue_instance = getattr(self.__modules[consumer_module]["instance"].queuepool, consumer_queue)
                break
            except :
                self.logging.info("Queue %s does not exist in module %s.  Autocreate queue."%(producer_queue, producer_module))

        self.__modules[consumer_module]["link"]=spawn (self.__forwardEvents, producer_queue_instance, consumer_queue_instance)

    def doRescue(self):
        '''Runs over each queue to extract any left behind messages.
        '''

        for module in reversed(self.__modules):
            for queue in module.queuepool.messagesLeft():
                for blah in module.queuepool.dump(queue):
                    print (blah)

    def register(self, module, *args, **kwargs):
        '''Registers a Wishbone actor into the router.
        '''

        if len(module) < 3:
            raise Exception("The module tuple requires 3 values.")

        limit = module[2]
        name = module[1]
        module = module[0]

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "link":None}

        if limit > 0:
            self.__modules[name]["instance"]=module(name, limit, *args, **kwargs)
        else:
            self.__modules[name]["instance"]=module(name, *args, **kwargs)

        # Start to forward this module's logs to the registered
        # logging module.
        self.__modules[name]["fwd_logs"] = spawn (self.__forwardLogs, self.__modules[name]["instance"].logging.logs, self.logs)

        # Start to forward this module's metrics to the registered
        # metrics module.
        self.__modules[name]["fwd_metrics"] = spawn (self.__gatherMetrics, self.__modules[name]["instance"])

    def registerLogModule(self, module, queue, *args, **kwargs):
        '''Registers and connects the module to the router's log queue.

        If this method is not called (no module connected to it) the queue is
        automatically connected to a Null module.

        Parameters:

            module(instance)        An initialized wishbone module.
            queue(str)              The name of the module's queue to connect to.
            *args(list)             Positional arguments to pass to thevmodule.
            **kwargs(dict)          Named arguments to pass to the module.
        '''

        if len(module) < 3:
            raise Exception("The module tuple requires 3 values.")

        limit = module[2]
        name = module[1]
        module = module[0]

        self.__logmodule = name

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "link":None}

        if limit > 0:
            self.__modules[name]["instance"]=module(name, limit, *args, **kwargs)
        else:
            self.__modules[name]["instance"]=module(name, *args, **kwargs)

        self.__modules[name]["fwd_logs"] = spawn (self.__forwardLogs, self.__modules[name]["instance"].logging.logs, self.logs)
        self.__modules[name]["fwd_metrics"] = spawn (self.__gatherMetrics, self.__modules[name]["instance"])

        try:
            queue = getattr(self.__modules[name]["instance"].queuepool, queue)
        except Exception:
            raise QueueMissing("Queue %s does not exist in module %s"%(queue, module))

        self.__modules[name]["link"] = spawn (self.__forwardEvents, self.logs, queue)

    def registerMetricModule(self, module, queue, *args, **kwargs):
        '''Registers and connects the module to the router's log queue.

        If this method is not called (no module connected to it) the queue is
        automatically connected to a Null module.
        Parameters:

            module(instance)        An initialized wishbone module.
            queue(str)              The name of the module's queue to connect to.
            *args(list)             Positional arguments to pass to thevmodule.
            **kwargs(dict)          Named arguments to pass to the module.
        '''

        if len(module) < 3:
            raise Exception("The module tuple requires 3 values.")

        limit = module[2]
        name = module[1]
        module = module[0]

        self.__metricmodule = name

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "link":None}

        if limit > 0:
            self.__modules[name]["instance"]=module(name, limit, *args, **kwargs)
        else:
            self.__modules[name]["instance"]=module(name, *args, **kwargs)


        self.__modules[name]["fwd_logs"] = spawn (self.__forwardLogs, self.__modules[name]["instance"].logging.logs, self.logs)
        self.__modules[name]["fwd_metrics"] = spawn (self.__gatherMetrics, self.__modules[name]["instance"])

        try:
            queue = getattr(self.__modules[name]["instance"].queuepool, queue)
        except Exception:
            raise QueueMissing("Queue %s does not exist in module %s."%(queue, module))

        self.__modules[name]["link"] = spawn (self.__forwardEvents, self.metrics, queue)

    def start(self):
        '''Starts the router and all registerd modules.

        Executes following steps:

            - Starts the registered logging module.
            - Starts the registered metrics module.
            - Calls each registered module's start() function.
        '''

        self.logging.info('Starting.')
        for module in self.__modules:
            self.__modules[module]["instance"].start()

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
        for module in self.__modules.keys():
            if module in [self.__logmodule, self.__metricmodule, "stdout"]:
                continue
            else:
                self.__modules[module]["instance"].stop()
                while self.__modules[module]["instance"].logging.logs.size() > 0:
                    sleep(0.5)

        while self.__modules[self.__logmodule]["instance"].queuepool.inbox.size() > 0 or self.logs.size() > 0:
            sleep(0.5)

        self.__runConsumers.set()

        if self.rescue:
            self.doRescue()

        self.__exit.set()

    def __gatherMetrics(self, module):

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
        cycler=0
        while not self.__runConsumers.isSet():
            cycler += 1
            try:
                data = producer.get()
            except:
                sleep(0.1)
            else:
                if self.__checkIntegrity(data):
                    try:
                        consumer.put(data)
                    except Exception as err:
                        producer.rescue(data)
                else:
                    self.logging.warn("Invalid event format.")
                    self.logging.debug("Invalid event format. %s"%(data))
            if cycler == 100:
                cycler=0
                sleep()

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
            sleep()

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
        #return True

        if type(event) is dict:
            if len(event.keys()) == 2:
                if "header" in event and "data" in event:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False