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

from wishbone.queue import Queue
from wishbone.queue import QueuePool
from wishbone.logging import Logging
from wishbone.error import QueueEmpty, QueueFull, ReservedName, QueueConnected
from gevent.pool import Group
from gevent import spawn
from gevent import sleep, socket
from gevent.event import Event
from time import time


class Actor():

    def __init__(self, name, size, frequency=1):

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

        setattr(instance.pool.queue, destination, self.pool.getQueue(source))
        self.pool.getQueue(source).disableFallThrough()

    def flushQueuesToDisk(self):
        '''Writes whatever event in the queue to disk for later retrieval.'''

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

    def start(self):
        '''Starts the module.'''

        self.readQueuesFromDisk()

        if hasattr(self, "preHook"):
            self.logging.debug("preHook() found, executing")
            self.preHook()

        self.__run.set()
        self.logging.info("Started")

    def stop(self):
        '''Kills all registered Consumers.'''

        self.__loop = False
        self.threads.join()

        if hasattr(self, "postHook"):
            self.logging.debug("postHook() found, executing")
            self.postHook()

        self.flushQueuesToDisk()

    def submit(self, event, queue):
        '''A convenience function which submits <event> to <queue>
        and deals with QueueFull and the module lock set to False.'''

        while self.loop():
            try:
                queue.put(event)
                break
            except QueueFull:
                queue.waitUntilFree()

    def __consumer(self, function, queue):
        '''Greenthread which applies <function> to each element from <queue>'''

        self.__run.wait()

        while self.loop():
            try:
                event = self.pool.queue.__dict__[queue].get()
            except QueueEmpty:
                self.pool.queue.__dict__[queue].waitUntilContent()
            else:
                try:
                    function(event)
                    self.submit(event, self.pool.queue.success)
                except Exception as err:
                    self.submit(event, self.pool.queue.failed)

    def __metricEmitter(self):
        '''A greenthread which collects the queue metrics at the defined interval.'''

        self.__run.wait()
        while self.loop():
            for queue in self.pool.listQueues(names=True):
                stats = self.pool.getQueue(queue).stats()
                for item in stats:
                    while self.loop():
                        try:
                            self.pool.queue.metrics.put({"header": {}, "data": (time(), "wishbone", socket.gethostname(), "queue.%s.%s.%s" % (self.name, queue, item), stats[item], '', ())})
                            break
                        except QueueFull:
                            self.pool.queue.metrics.waitUntilFree()
            sleep(self.frequency)
