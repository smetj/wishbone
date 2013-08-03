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
from wishbone.tools import LoopContextSwitcher
from wishbone.errors import QueueMissing, QueueOccupied, SetupError, QueueFull, QueueLocked
from gevent import spawn, sleep, signal, joinall, kill, Greenlet
from gevent.event import Event
from collections import OrderedDict
from uuid import uuid4

class Default(LoopContextSwitcher):
    '''The default Wishbone router.

    A router is responsible to:

        - Forward the events from one queue to the other.
        - Forward the logs from all modules to the logging module
        - Forward the metrics from all modules to the metrics module.

    SIGINT is intercepted and initiates a proper shutdown sequence.

    Parameters:

        - interval(int):    The interval metrics are polled from each module

        - context_switch(int):  How many events to shuffle from queue to
                                queue before issuing a context switch.
                                Default: 100

        - rescue(bool):     Whether to extract any events stuck in one of
                            the queues and write that to a cache file.  Next
                            startup the events are read from the cache and
                            inserted into the same queue again.

        - uuid(bool):       If True, adds a uuid4 value in the header of each
                            event if not present when forwarded from one queue
                            to the other. (default False)

    '''

    def __init__(self, interval=10, context_switch=100, rescue=False, uuid=False):
        self.interval=interval
        self.context_switch=context_switch
        self.rescue=rescue

        signal(2, self.__signal_handler)
        self.logging=QLogging("Router")
        self.logs=WishboneQueue()
        self.metrics=WishboneQueue()

        if uuid == True:
            self.__UUID = self.__doUUID
        else:
            self.__UUID = self.__noUUID

        # Forward router's logs to logging queue.
        #########################################
        spawn (self.__forwardEvents, self.logging.logs, self.logs)

        self.__modules = {}
        self.__logmodule = None
        self.__metricmodule = None
        self.__map=[]

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
        '''Connects a producing queue to a consuming queue.

        A separate greenthread consumes the events from the consumer queue and
        submits these to the producer queue. When a non existing queue is
        defined, it is autocreated.

        The notation of queue names is:

            modulename.queuename

        Parameters:

            producer(string):   The name of the producing module queue.
            consumer(string):   The name of the consumnig module queue.

        '''

        try:
            (producer_module, producer_queue) = producer.split(".")
        except ValueError:
            raise Exception("A queue name should have format 'module.queue'. Got '%s' instead"%(producer))

        try:
            (consumer_module, consumer_queue) = consumer.split(".")
        except ValueError:
            raise Exception("A queue name should have format 'module.queue'. Got '%s' instead"%(consumer))

        self.__modules[producer_module]["children"].append(consumer_module)

        if not self.__modules.has_key(producer_module):
            raise Exception("There is no Wishbone module registered with name '%s'"%(producer_module))
        if not self.__modules.has_key(consumer_module):
            raise Exception("There is no Wishbone module registered with name '%s'"%(consumer_module))

        while True:
            try:
                producer_queue_instance = getattr(self.__modules[producer_module]["instance"].queuepool, producer_queue)
                break
            except:
                self.logging.info("Queue %s does not exist in module %s.  Autocreate queue."%(producer_queue, producer_module))
                self.__modules[producer_module]["instance"].createQueue(producer_queue)

        while True:
            try:
                consumer_queue_instance = getattr(self.__modules[consumer_module]["instance"].queuepool, consumer_queue)
                break
            except :
                self.logging.info("Queue %s does not exist in module %s.  Autocreate queue."%(producer_queue, producer_module))
                self.__modules[consumer_module]["instance"].createQueue(consumer_queue)

        if self.__modules[consumer_module]["connections"].has_key(consumer_queue):
            raise QueueOccupied("Queue %s of module %s is already connected."%(consumer_queue, consumer_module))

        if self.__modules[producer_module]["connections"].has_key(producer_queue):
            raise QueueOccupied("Queue %s of module %s is already connected."%(producer_queue, producer_module))

        self.__modules[consumer_module]["connections"]={}

        self.__modules[consumer_module]["connections"][consumer_queue]=spawn (self.__forwardEvents, producer_queue_instance, consumer_queue_instance)
        #store a reference of the greenthread to the other side.
        self.__modules[producer_module]["connections"][producer_queue]=self.__modules[consumer_module]["connections"][consumer_queue]

    def getChildren(self, instance):
        children=[]

        def getChild(instance, children):
            if len(self.__modules[instance]["children"]) > 0:
                for child in self.__modules[instance]["children"]:
                    getChild(child, children)
                    children.append(child)

        getChild(instance, children)
        return children

    def doRescue(self):
        '''Runs over each queue to extract any left behind messages.
        '''

        for module in reversed(self.__modules):
            for queue in module.queuepool.messagesLeft():
                for blah in module.queuepool.dump(queue):
                    print (blah)

    def loop(self):

        '''Convenience funtion which returns a bool indicating the router is in running or stop state.'''

        return not self.__runConsumers.isSet()

    def register(self, module, *args, **kwargs):
        '''Registers a Wishbone actor into the router.
        '''

        if len(module) < 3:
            raise Exception("The module tuple requires 3 values.")

        limit = int(module[2])
        name = module[1]
        module = module[0]

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "connections":{}, "children":[]}

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

    def registerLogModule(self, module, *args, **kwargs):
        '''Registers and connects the module to the router's log queue.

        If this method is not called (no module connected to it) the queue is
        automatically connected to a Null module.

        Parameters:

            module(instance)        An initialized wishbone module.
            *args(list)             Positional arguments to pass to thevmodule.
            **kwargs(dict)          Named arguments to pass to the module.
        '''

        if len(module) < 3:
            raise SetupError("The module tuple requires 3 values.")

        limit = module[2]
        name = module[1]
        module = module[0]

        self.__logmodule = name

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "connections":{}, "children": []}

        if limit > 0:
            self.__modules[name]["instance"]=module(name, limit, *args, **kwargs)
        else:
            self.__modules[name]["instance"]=module(name, *args, **kwargs)

        self.__modules[name]["fwd_logs"] = spawn (self.__forwardLogs, self.__modules[name]["instance"].logging.logs, self.logs)
        self.__modules[name]["fwd_metrics"] = spawn (self.__gatherMetrics, self.__modules[name]["instance"])

        self.__modules[name]["connections"]["inbox"] = spawn (self.__forwardEvents, self.logs, self.__modules[name]["instance"].queuepool.inbox)

    def registerMetricModule(self, module, *args, **kwargs):
        '''Registers and connects the module to the router's log queue.

        If this method is not called (no module connected to it) the queue is
        automatically connected to a Null module.
        Parameters:

            module(instance)        An initialized wishbone module.
            *args(list)             Positional arguments to pass to thevmodule.
            **kwargs(dict)          Named arguments to pass to the module.
        '''

        if len(module) < 3:
            raise SetupERror("The module tuple requires 3 values.")

        limit = module[2]
        name = module[1]
        module = module[0]

        self.__metricmodule = name

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "connections":{}, "children": []}

        if limit > 0:
            self.__modules[name]["instance"]=module(name, limit, *args, **kwargs)
        else:
            self.__modules[name]["instance"]=module(name, *args, **kwargs)


        self.__modules[name]["fwd_logs"] = spawn (self.__forwardLogs, self.__modules[name]["instance"].logging.logs, self.logs)
        self.__modules[name]["fwd_metrics"] = spawn (self.__gatherMetrics, self.__modules[name]["instance"])
        self.__modules[name]["connections"]["inbox"] = spawn (self.__forwardEvents, self.metrics, self.__modules[name]["instance"].queuepool.inbox)

    def start(self):
        '''Starts the router and all registerd modules.

        Executes following steps:

            - Starts the registered logging module.
            - Starts the registered metrics module.
            - Calls each registered module's start() function.
        '''

        self.logging.info('Starting.')
        for module in self.__modules:
            try:
                self.__modules[module]["instance"].preHook()
                self.logging.debug("Prehook found for module %s and executed."%(module))
            except AttributeError:
                self.logging.debug("Prehook not found for module %s."%(module))

            self.__modules[module]["instance"].start()

    def stop(self):
        '''Stops the router and all registered modules.

        It stops all the modules except the modules connected
        to the logs or metrics endpoint to ensure these event
        streams survive untill the end.  All other modules
        are shutdown in the order they have been registered.
        '''

        self.logging.info('Stopping.')

        for module in self.__modules.keys():
            if module in [self.__logmodule, self.__metricmodule]+self.getChildren(self.__logmodule)+self.getChildren(self.__metricmodule):
                continue
            else:
                try:
                    self.__modules[module]["instance"].postHook()
                    self.logging.debug("Posthook found for module %s and executed."%(module))
                except AttributeError:
                    self.logging.debug("Posthook not found for module %s."%(module))

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

    def __forwardEvents(self, source, destination):

        '''The background greenthread which continuously consumes the producing
        queue and dumps that data into the consuming queue.'''

        #todo(smetj): make this cycler setup more dynamic?  Auto adjust the amount
        #cycles before context switch to achieve sweetspot?

        context_switch_loop = self.getContextSwitcher(self.context_switch, self.loop)

        while context_switch_loop.do():
            try:
                event = source.get()
            except QueueLocked:
                source.waitUntilGetAllowed()
            else:
                if self.__checkIntegrity(event):
                    event=self.__UUID(event)
                    try:
                        destination.put(event)
                    except QueueLocked:
                        source.putLock()
                        source.rescue(event)
                        destination.waitUntilPutAllowed()
                        source.putUnlock()
                    except QueueFull:
                        source.putLock()
                        source.rescue(event)
                        destination.waitUntilFreePlace()
                        source.putUnlock()
                else:
                    self.logging.warn("Invalid event format.")
                    self.logging.debug("Invalid event format. %s"%(event))

    def __forwardLogs(self, source, destination):

        '''The background greenthread which continuously consumes the producing
        queue and dumps that data into the consuming queue.'''

        #todo(smetj): When not context switching logs are more serialized instead
        #of interleaved.  Might have to give it some though whether this is an
        #issue or not.

        context_switch_loop = self.getContextSwitcher(10, self.loop)

        while context_switch_loop.do():
            try:
                event = source.get()
            except:
                sleep(0.1)
            else:
                if self.__checkIntegrity(event):
                    try:
                        destination.put(event)
                    except:
                        source.rescue(event)
                else:
                    self.logging.warn("Invalid event format.")
                    self.logging.debug("Invalid event format. %s"%(event))

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
                if "header" in event and "data" in event:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def __doUUID(self, event):
        try:
            event["header"]["uuid"]
        except:
            event["header"]["uuid"] = str(uuid4())
        return event

    def __noUUID(self, event):
        return event

