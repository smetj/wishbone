#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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
from wishbone.error import QueueEmpty, QueueFull, QueueConnected
from gevent.pool import Group
from gevent import spawn
from gevent import sleep, socket
from gevent.event import Event
from time import time
from copy import copy
from sys import exc_info
import traceback


class Actor():

    def __init__(self, name, size=100, frequency=1):

        self.name = name
        self.size = size
        self.frequency = frequency

        self.pool = QueuePool(size)

        self.logging = Logging(name, self.pool.queue.logs)

        self.__loop = True
        self.threads = Group()

        spawn(self.__metricEmitter)

        self.__run = Event()
        self.__run.clear()

        self.__connections = {}

        self.__children = {}
        self.__parents = {}

        self.__adminConsumer_active = False
        self.__adminConsumers = {}

    def connect(self, source, instance, destination):
        '''Connects the <source> queue to the <destination> queue.
        In fact, the source queue overwrites the destination queue.'''

        if source in self.__children:
            raise QueueConnected("Queue %s is already connected to %s." % (source, self.__children[source]))
        else:
            self.__children[source] = "%s.%s" % (instance.name, destination)

        if destination in instance.__parents:
            raise QueueConnected("Queue %s.%s is already connected to %s" % (instance.name, destination, instance.__parents[destination]))
        else:
            instance.__parents[destination] = "%s.%s" % (self.name, source)

        if not self.pool.hasQueue(source):
            self.pool.createQueue(source)

        setattr(instance.pool.queue, destination, self.pool.getQueue(source))
        self.pool.getQueue(source).disableFallThrough()

    def createEvent(self):

        '''Convenience function which returns an empty     Wishbone event with the
        current namespace already set.'''

        return Wishbone_Event(self.name)

    def flushQueuesToDisk(self):
        '''Writes whatever event in the queue to disk for later retrieval.'''

        # for queue in self.pool.listQueues(names=True):
        #     size = self.pool.getQueue(queue).size()
        #     print "%s %s %s" % (self.name, queue, size)

        self.logging.debug("Writing queues to disk.")

    def getChildren(self, queue=None):
        '''Returns the queue name <queue> is connected to.'''

        if queue is None:
            return [self.__children[q] for q in self.__children.keys()]
        else:
            return self.__children[queue]

    def loop(self):
        '''The global lock for this module'''

        return self.__loop

    def readQueuesFromDisk(self):
        '''Reads events from disk into the queue.'''

        self.logging.debug("Reading queues from disk.")

    def registerConsumer(self, function, queue):
        '''Registers <function> to process all events in <queue>

        Do not trap errors.  When <function> fails then the event will be
        submitted to the "failed" queue,  If <function> succeeds to the
        success queue.'''

        consumer = self.threads.spawn(self.__consumer, function, queue)
        consumer.function = function.__name__
        consumer.queue = queue

    def registerAdminCallback(self, function):
        '''Registers <function> to respond to the incoming admin messages.'''

        if not self.__adminConsumer_active:
            spawn(self.__adminConsumer)

    def start(self):
        '''Starts the module.'''

        # self.readQueuesFromDisk()

        if hasattr(self, "preHook"):
            self.logging.debug("preHook() found, executing")
            self.preHook()

        self.__run.set()
        self.logging.debug("Started with max queue size of %s events and metrics interval of %s seconds." % (self.size, self.frequency))

    def stop(self):
        '''Stops the loop lock and waits until all registered consumers have exit.'''

        self.__loop = False
        self.threads.join()

        if hasattr(self, "postHook"):
            self.logging.debug("postHook() found, executing")
            self.postHook()

    def submit(self, event, queue):
        '''A convenience function which submits <event> to <queue>
        and deals with QueueFull and the module lock set to False.'''

        while self.loop():
            try:
                queue.put(event)
                break
            except QueueFull as err:
                err.waitUntilEmpty()

    def __adminConsumer(self):
        '''Greenthread which consumes the admin queue.'''

        self.__adminConsumer_active = True
        self.__run.wait()
        self.logging.debug("adminConsumer started.")
        while self.loop():
            try:
                command = self.pool.queue.admin.get()
            except QueueEmpty as err:
                err.waitUntilContent()
            else:
                print command

    def __consumer(self, function, queue):
        '''Greenthread which applies <function> to each element from <queue>
        '''

        self.__run.wait()

        while self.loop():
            try:
                event = self.pool.queue.__dict__[queue].get()
            except QueueEmpty as err:
                err.waitUntilContent()
            else:
                event.initNamespace(self.name)
                try:
                    function(event)
                except QueueFull as err:
                    self.pool.queue.__dict__[queue].rescue(event)
                    err.waitUntilFree()
                except Exception as err:
                    exc_type, exc_value, exc_traceback = exc_info()
                    event.setErrorValue(self.name, traceback.extract_tb(exc_traceback)[-1][1], str(exc_type), str(exc_value))
                    self.submit(event, self.pool.queue.failed)
                else:
                    self.submit(event, self.pool.queue.success)

    def __metricEmitter(self):
        '''A greenthread which collects the queue metrics at the defined interval.'''

        hostname = socket.gethostname()
        self.__run.wait()
        while self.loop():
            for queue in self.pool.listQueues(names=True):
                stats = self.pool.getQueue(queue).stats()
                for item in stats:
                    while self.loop():
                        try:
                            event = Wishbone_Event("metric:%s" % self.name)
                            event.data = (time(), "wishbone", hostname, "queue.%s.%s.%s" % (self.name, queue, item), stats[item], '', ())
                            self.pool.queue.metrics.put(event)
                            break
                        except QueueFull as err:
                            err.waitUntilFree()
            sleep(self.frequency)
