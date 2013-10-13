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

from wishbone.tools import QLogging
from wishbone.tools import WishboneQueue
from wishbone.tools import LoopContextSwitcher
from wishbone.errors import QueueMissing, QueueOccupied, SetupError, QueueFull, QueueLocked
from gevent import spawn, sleep, signal, joinall, kill, Greenlet
from gevent.event import Event
from uuid import uuid4
from time import time
from os.path import basename
from sys import argv

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

        - throttle(bool):   If True, scans every second for modules which
                            overflow child modules with messages and thus have
                            to be throttled.
                            default: False

        - throttle_threshold(int):  When <throttle> is True, start to throttle
                                    start to throttle when a module has more
                                    than <throttle_threshold> messages.
                                    default: 5000

    '''

    def __init__(self, interval=10, context_switch=100, rescue=False, uuid=False, throttle=False, throttle_threshold=5000):
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

        self.__throttle=throttle
        self.__throttle_threshold=throttle_threshold

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

        self.script_name = basename(argv[0]).replace(".py","")

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

        The syntax of queue names is:

            module_instance_name.queuename

        Parameters:

            - producer(str):   The name of the producing module queue.

            - consumer(str):   The name of the consuming module queue.

        '''

        try:
            (producer_module, producer_queue) = producer.split(".")
        except ValueError:
            raise Exception("A queue name should have format 'module.queue'. Got '%s' instead"%(producer))

        try:
            (consumer_module, consumer_queue) = consumer.split(".")
        except ValueError:
            raise Exception("A queue name should have format 'module.queue'. Got '%s' instead"%(consumer))

        try:
            self.__modules[producer_module]
        except:
            raise Exception ("There is no module registered with name %s"%(producer_module))

        try:
            self.__modules[consumer_module]
        except:
            raise Exception ("There is no module registered with name %s"%(consumer_module))

        self.__modules[producer_module]["children"].append(consumer_module)
        self.__modules[consumer_module]["parents"].append(producer_module)

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
                self.logging.info("Queue %s does not exist in module %s.  Autocreate queue."%(consumer_queue, consumer_module))
                self.__modules[consumer_module]["instance"].createQueue(consumer_queue)

        if self.__modules[consumer_module]["connections"].has_key(consumer_queue):
            raise QueueOccupied("Queue %s of module %s is already connected."%(consumer_queue, consumer_module))

        if self.__modules[producer_module]["connections"].has_key(producer_queue):
            raise QueueOccupied("Queue %s of module %s is already connected."%(producer_queue, producer_module))

        self.__modules[consumer_module]["connections"]={}

        self.__modules[consumer_module]["connections"][consumer_queue]=producer_queue
        self.__modules[producer_module]["connections"][producer_queue]=consumer_queue

        #self.__modules[producer_module]["instance"].queuepool.outbox=self.__modules[consumer_module]["instance"].queuepool.inbox
        setattr(self.__modules[producer_module]["instance"].queuepool, producer_queue, consumer_queue_instance)


    def getChildren(self, instance):
        children=[]

        def getChild(instance, children):
            if len(self.__modules[instance]["children"]) > 0:
                for child in self.__modules[instance]["children"]:
                    getChild(child, children)
                    children.append(child)

        getChild(instance, children)
        return children

    def getParents(self, instance):
        parents=[]

        def getParent(instance, parents):
            if len(self.__modules[instance]["parents"]) > 0:
                for parent in self.__modules[instance]["parents"]:
                    getParent(parent, parents)
                    parents.append(parent)

        getParent(instance, parents)
        return parents

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

    def register(self, module, name, *args, **kwargs):
        '''Registers a Wishbone actor into the router.

        Parameters:

            module(module)          A wishbone module.
            name(string)            The name to assign to the module insance.
            args(list)              Positional arguments to pass to the module.
            kwargs(dict)            Named arguments to pass to the module.
        '''

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "connections":{}, "children":[], "parents":[]}
        self.__modules[name]["instance"]=module(name, *args, **kwargs)

        self.__modules[name]["fwd_logs"] = spawn (self.__forwardLogs, self.__modules[name]["instance"].logging.logs, self.logs)
        self.__modules[name]["fwd_metrics"] = spawn (self.__gatherMetrics, self.__modules[name]["instance"])

    def registerLogModule(self, module, name, *args, **kwargs):
        '''Registers and connects the module to the router's log queue.

        If this method is not called (no module connected to it) the queue is
        automatically connected to a Null module.

        Parameters:

            module(module)          A wishbone module.
            name(string)            The name to assign to the module insance.
            args(list)              Positional arguments to pass to the module.
            kwargs(dict)            Named arguments to pass to the module.
        '''

        self.__logmodule = name

        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "connections":{}, "children": [], "parents":[]}
        self.__modules[name]["instance"]=module(name, *args, **kwargs)

        self.__modules[name]["fwd_logs"] = spawn (self.__forwardLogs, self.__modules[name]["instance"].logging.logs, self.logs)
        self.__modules[name]["fwd_metrics"] = spawn (self.__gatherMetrics, self.__modules[name]["instance"])

        self.__modules[name]["connections"]["inbox"] = spawn (self.__forwardEvents, self.logs, self.__modules[name]["instance"].queuepool.inbox)

    def registerMetricModule(self, module, name, *args, **kwargs):
        '''Registers and connects the module to the router's log queue.

        If this method is not called (no module connected to it) the queue is
        automatically connected to a Null module.

        Parameters:

            module(module)          A wishbone module.
            name(string)            The name to assign to the module insance.
            args(list)              Positional arguments to pass to the module.
            kwargs(dict)            Named arguments to pass to the module.
        '''

        self.__metricmodule = name
        self.__modules[name] = {"instance":None, "fwd_logs":None, "fwd_metrics":None, "connections":{}, "children": [], "parents": []}
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

        if self.__logmodule == None:
            from wishbone.module import Null
            self.registerLogModule(Null, "__null_logs")

        if self.__metricmodule == None:
            from wishbone.module import Null
            self.registerMetricModule(Null, "__null_metrics")

        for module in self.__modules:
            try:
                self.__modules[module]["instance"].preHook()
                self.logging.debug("Prehook found for module %s and executed."%(module))
            except AttributeError:
                self.logging.debug("Prehook not found for module %s."%(module))

            self.__modules[module]["instance"].start()

        if self.__throttle == True:
            self.logging.info("Throttling enabled.  Starting throttle monitor.")
            spawn(self.throttleMonitor)

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
        the registered metrics module.


        Metrics have following format:

            (time, type, source, name, value, unit, (tag1, tag2))
        '''

        while not self.__runConsumers.isSet():
            now = time()
            if hasattr(module, "metrics"):
                for fn in module.metrics:
                    metric=(now, "wishbone", self.script_name, "function.%s.%s.total_time"%(module.name, fn), module.metrics[fn]["total_time"], '',())
                    self.metrics.put({"header":{}, "data":metric})
                    metric=(now, "wishbone", self.script_name, "function.%s.%s.hits"%(module.name, fn), module.metrics[fn]["hits"], '',())
                    self.metrics.put({"header":{}, "data":metric})

            for queue in module.queuepool.listQueues():
                stats = getattr(module.queuepool, queue).stats()
                for item in stats:
                    metric=(now, "wishbone", self.script_name, "queue.%s.%s.%s"%(module.name, queue, item), stats[item], '', ())
                    self.metrics.put({"header":{}, "data":metric})
            sleep(self.interval)

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

    def __doUUID(self, event):
        try:
            event["header"]["uuid"]
        except:
            event["header"]["uuid"] = str(uuid4())
        return event

    def __noUUID(self, event):
        return event

    def throttleMonitor(self):
        """Sweeps over all registered modules and tries to detect modules with  problematic flow rates.
        Once found a moduleMonitor greenthread is spawned which is reponsible for enabling and disabling
        throttling."""

        active_module_monitors={}

        while self.loop():
            for module in self.__modules:
                for queue in self.__modules[module]["instance"].queuepool.listQueues():
                    if getattr(self.__modules[module]["instance"].queuepool, queue).size() > self.__throttle_threshold:
                        parents = self.getParents(module)
                        if len(parents) == 0:
                            #simple, the module is flooding itself.
                            if module in active_module_monitors and active_module_monitors[module].ready():
                                active_module_monitors[module] = spawn(self.moduleMonitor, module, module, getattr(self.__modules[module]["instance"].queuepool, queue).size)
                        else:
                            #We have to find the upstream culprit responsible for flooding.
                            #A parent module with a queue with the highest out_rate
                            if parents[0] not in active_module_monitors or parents[0] in active_module_monitors and active_module_monitors[parents[0]].ready():
                                active_module_monitors[parents[0]] = spawn(self.moduleMonitor, parents[0], module, getattr(self.__modules[module]["instance"].queuepool, queue).size)
            sleep(1)

    def moduleMonitor(self, module, child_name, child_size):
        """A moduleMonitor is a greenthread which monitors the state of a module and triggers the expected
        throttling functions.  It exits when no more throttling is required.
        """

        self.logging.info("Module %s is identified to overflow module %s. Enable throttling."%(module, child_name))
        while self.loop():
            if child_size() > self.__throttle_threshold:
                try:
                    self.__modules[module]["instance"].enableThrottling()
                    sleep(1)
                except:
                    self.logging.info("Throttling is requested but module has no enableThrottling() function.")
                    break
            else:
                try:
                    self.__modules[module]["instance"].disableThrottling()
                    self.logging.info("Throttling on module %s is not required anymore. Exiting."%(module))
                except:
                    self.logging.info("Throttling is requested but module has no disableThrottling() function.")
                break
            sleep(1)

    # def statsMonitor(self):
    #     while self.loop():
    #         for module in self.__modules:
    #             for queue in self.__modules[module]["instance"].queuepool.listQueues():
    #                 print "%s.%s: %s"%(module, queue, str(getattr(self.__modules[module]["instance"].queuepool, queue).stats()))
    #         print
    #         sleep(1)
