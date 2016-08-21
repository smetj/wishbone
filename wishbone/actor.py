#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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

from wishbone.queue import QueuePool
from wishbone.logging import Logging
from wishbone.event import Event as Wishbone_Event
from wishbone.event import Metric
from wishbone.event import Bulk
from wishbone.error import QueueConnected, ModuleInitFailure
from wishbone.lookup import EventLookup
from uplook.errors import NoSuchValue
from collections import namedtuple
from gevent import spawn, kill
from gevent import sleep, socket
from gevent.event import Event
from wishbone.error import QueueFull
from time import time
from sys import exc_info
from uplook import UpLook
import traceback
import inspect

Greenlets = namedtuple('Greenlets', "consumer generic log metric")

class ActorConfig(object):

    '''
    A configuration object pass to a Wishbone actor.

    This is a simple object which holds a set of attributes (with some sane
    defaults) a Wishbone Actor expects.

    Attributes:
        name (str): The name identifying the actor instance.
        size (int): The size of the Actor instance's queues.
        frequency (int): The time in seconds to generate metrics.
        lookup (dict): A dictionary of lookup methods.
        description (str): A short free form discription of the actor instance.

    '''

    def __init__(self, name, size=100, frequency=1, lookup={}, description="A Wishbone actor."):

        '''

        Args:
            name (str): The name identifying the actor instance.
            size (int): The size of the Actor instance's queues.
            frequency (int): The time in seconds to generate metrics.
            lookup (dict): A dictionary of lookup methods.
            description (str): A short free form discription of the actor instance.

        '''
        self.name = name
        self.size = size
        self.frequency = frequency
        self.lookup = lookup
        self.description = description


class Actor():

    def __init__(self, config):

        self.config = config
        self.name = config.name
        self.size = config.size
        self.frequency = config.frequency
        self.description = config.description

        self.pool = QueuePool(config.size)

        self.logging = Logging(config.name, self.pool.queue.logs)

        self.__loop = True
        self.greenlets = Greenlets([], [], [], [])
        self.greenlets.metric.append(spawn(self.metricProducer))

        self.__run = Event()
        self.__run.clear()

        self.__connections = {}

        self.__children = {}
        self.__parents = {}

        self.__lookups = {}

        self.__buildUplook()

        self.stopped = True

    def connect(self, source, destination_module, destination_queue):
        '''Connects the <source> queue to the <destination> queue.
        In fact, the source queue overwrites the destination queue.'''

        if source in self.__children:
            raise QueueConnected("Queue %s.%s is already connected to %s." % (self.name, source, self.__children[source]))
        else:
            self.__children[source] = "%s.%s" % (destination_module.name, destination_queue)

        if destination_queue in destination_module.__parents:
            raise QueueConnected("Queue %s.%s is already connected to %s" % (destination_module.name, destination_queue, destination_module.__parents[destination_queue]))
        else:
            destination_module.__parents[destination_queue] = "%s.%s" % (self.name, source)

        if not self.pool.hasQueue(source):
            self.pool.createQueue(source)

        setattr(destination_module.pool.queue, destination_queue, self.pool.getQueue(source))
        self.pool.getQueue(source).disableFallThrough()
        self.logging.debug("Connected queue %s.%s to %s.%s" % (self.name, source, destination_module.name, destination_queue))

    def doEventLookup(self, name):

        try:
            return self.current_event.get(name)
        except AttributeError:
            return ""
        except KeyError:
            # No event has passed through this module.  Most likely this is an
            # input module which creates its own events. Therefor there is
            # nothing to lookup yet and there for we rely up UpLook to return
            # the default value for this lookup if any.
            self.logging.debug("There is no lookup value with name '%s' Falling back to default lookup value if any." % (name))
            raise NoSuchValue

    def getChildren(self, queue=None):
        '''Returns the queue name <queue> is connected to.'''

        if queue is None:
            return [self.__children[q] for q in list(self.__children.keys())]
        else:
            return self.__children[queue]

    def loop(self):
        '''The global lock for this module'''

        return self.__loop

    def postHook(self):

        pass

    def preHook(self):

        self.logging.debug("Initialized.")

    def registerConsumer(self, function, queue):
        '''Registers <function> to process all events in <queue>

        Do not trap errors.  When <function> fails then the event will be
        submitted to the "failed" queue,  If <function> succeeds to the
        success queue.'''

        self.greenlets.consumer.append(spawn(self.__consumer, function, queue))

    def start(self):
        '''Starts the module.'''

        if hasattr(self, "preHook"):
            self.logging.debug("preHook() found, executing")
            self.preHook()

        self.__run.set()
        self.logging.debug("Started with max queue size of %s events and metrics interval of %s seconds." % (self.size, self.frequency))
        self.stopped = False

    def sendToBackground(self, function, *args, **kwargs):
        '''Executes a function and sends it to the background.'''

        self.greenlets.generic.append(spawn(function, *args, **kwargs))
        sleep()

    def stop(self):
        '''Stops the loop lock and waits until all registered consumers have exit otherwise kills them.'''

        self.logging.info("Received stop. Initiating shutdown.")

        self.__loop = False

        for background_job in self.greenlets.metric:
            kill(background_job)

        for background_job in self.greenlets.generic:
            kill(background_job)

        for background_job in self.greenlets.consumer:
            kill(background_job)

        if hasattr(self, "postHook"):
            self.logging.debug("postHook() found, executing")
            self.postHook()

        self.logging.debug("Exit.")

        self.stopped = True

    def submit(self, event, queue):
        '''A convenience function which submits <event> to <queue>.'''

        while self.loop():
            try:
                queue.put(event)
                break
            except QueueFull:
                sleep(0.1)

    def __consumer(self, function, queue):
        '''Greenthread which applies <function> to each element from <queue>
        '''

        self.__run.wait()

        while self.loop():
            event = self.pool.queue.__dict__[queue].get()
            self.current_event = event
            try:
                function(event)
            except Exception as err:
                exc_type, exc_value, exc_traceback = exc_info()
                info = (traceback.extract_tb(exc_traceback)[-1][1], str(exc_type), str(exc_value))

                if isinstance(event, Wishbone_Event):
                    event.set(info, "@errors.%s" % (self.name))
                elif(event, Bulk):
                    event.error = info

                self.logging.error("%s" % (err))
                self.submit(event, self.pool.queue.failed)
            else:
                self.submit(event, self.pool.queue.success)

    def __buildUplook(self):

        self.__current_event = {}
        args = {}
        for key, value in list(inspect.getouterframes(inspect.currentframe())[2][0].f_locals.items()):
            if key == "self" or isinstance(value, ActorConfig):
                next
            else:
                args[key] = value

        uplook = UpLook(**args)
        for name in uplook.listFunctions():
            if name not in self.config.lookup:
                raise ModuleInitFailure("A lookup function '%s' was defined but no lookup function with that name registered." % (name))
            else:
                if self.config.lookup[name].__self__.__class__ == EventLookup:
                    uplook.registerLookup(name, self.doEventLookup)
                else:
                    uplook.registerLookup(name, self.config.lookup[name])

        self.uplook = uplook
        self.kwargs = uplook.get()

    def metricProducer(self):
        '''A greenthread which collects the queue metrics at the defined interval.'''

        self.__run.wait()
        hostname = socket.gethostname()
        while self.loop():
            for queue in self.pool.listQueues(names=True):
                for metric, value in list(self.pool.getQueue(queue).stats().items()):
                    metric = Metric(time=time(),
                                    type="wishbone",
                                    source=hostname,
                                    name="module.%s.queue.%s.%s" % (self.name, queue, metric),
                                    value=value,
                                    unit="",
                                    tags=())
                    event = Wishbone_Event(metric)
                    self.submit(event, self.pool.queue.metrics)
            sleep(self.frequency)
