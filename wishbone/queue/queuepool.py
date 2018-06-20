#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  queuepool.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from wishbone.error import QueuePoolError, QueueEmpty, QueueFull
from gevent import spawn, sleep
from gevent.event import Event
from .memoryqueue import MemoryQueue


class Shovel(object):
    def __init__(self, source_name, source, destination_name, destination):

        self.source_name = source_name
        self.source = source
        self.destination = destination
        self.destination_name = destination_name
        self.lock = True
        self.__pause = Event()
        self.__pause.set()

    def pause(self):
        """
        Pauses shoveling
        """

        self.__pause.clear()

    def start(self, *args, **kwargs):
        """
        Starts shoveling from source to destination

        Args:
            n/a

        Returns:
            None

        Raises:
            n/a
        """

        self.shovel = spawn(self.__shovel)

    def stop(self):

        self.lock = False
        self.shovel.join()

    def unpause(self):
        """
        Unpauses shoveling
        """

        self.__pause.set()

    def __shovel(self):
        # TODO(smetj): I assume more guarantees need to be foreseen here
        while self.lock:
            try:
                event = self.source.get(timeout=1)
            except QueueEmpty:
                continue

            while self.lock:
                try:
                    self.destination.put(event, timeout=1)
                    break
                except QueueFull:
                    continue

        self.source.enableFallThrough()
        self.destination.enableFallThrough()

    def __repr__(self):

        if self.lock:
            return "Running Shovel(%s -> %s)" % (
                self.source_name,
                self.destination_name,
            )
        else:
            return "Stopped Shovel(%s -> %s)" % (
                self.source_name,
                self.destination_name,
            )


class QueuePool(object):
    def __init__(self):
        """
           self.queues[target]["shovel"].stop()
            self.queues[target]["shovel"] = None
            self.queues[target]["destination"] = None
     Holds all queues and organizes shoveling data from one to the other.

        Args:
            None
        """

        self.queues = {}
        self.connections = {}

        # self.stats = spawn(self.__stats)

    def connect(self, source, destination):
        """
        Connects one module queue to the other in order to shovel messages over.

        Args:
            source (str): The name of the source module queue
            destination (str): The name of the destination module queue

        Returns:
            n/a

        Raises:
            QueuePoolError: A problem occured connecting the queues.
        """

        if not self.hasQueue(source):
            self.registerQueue(source, MemoryQueue())

        if not self.hasQueue(destination):
            self.registerQueue(destination, MemoryQueue())

        if self.isConnected(source):
            raise QueuePoolError(
                "Queue '%s' is already connected to '%s'"
                % (source, self.getConnectedQueue(source))
            )

        if self.isConnected(destination):
            raise QueuePoolError(
                "Queue '%s' is already connected to '%s'"
                % (destination, self.getConnectedQueue(destination))
            )

        source_queue_instance = self.getQueue(source)
        source_queue_instance.disableFallThrough()
        destination_queue_instance = self.getQueue(destination)
        destination_queue_instance.disableFallThrough()

        shovel = Shovel(
            source_name=source,
            source=source_queue_instance,
            destination_name=destination,
            destination=destination_queue_instance,
        )
        self.connections[(source, destination)] = shovel
        self.connections[(destination, source)] = shovel
        shovel.start()

    def getDirection(self, name):
        """
        Returns the flow direction of a connected queue

        Args:
            name (str): The name of the connected queue.

        Returns:
            str: Either "in" or "out"

        Raises:
            QueuePoolError: Something went wrong with the method
        """

        shovel = self.getConnection(name)
        if shovel.source_name == name:
            return "out"
        else:
            return "in"

    def disconnect(self, name):
        """
        Disconnects the refered queue.

        Args:
            name (str): The name of the module queue to disconnect

        Returns:
            n/a

        Raises:
            QueuePoolError: A problem occured disconnecting the queue.
        """

        if not self.hasQueue(name):
            raise QueuePoolError("There is no queue registered with name '%s'" % (name))

        if not self.isConnected(name):
            raise QueuePoolError("Queue '%s' is not connected." % (name))

        connected_queue = self.getConnectedQueue(name)

        self.connections[(name, connected_queue)].stop()
        del (self.connections[(name, connected_queue)])
        del (self.connections[(connected_queue, name)])
        self.getQueue(name).enableFallThrough()
        self.getQueue(connected_queue).enableFallThrough()

    def getConnection(self, name):
        """
        Returns the shovel object for the referred queue.

        Args:
            name (str): The name of the queue.

        Returns:
            Shovel: The shovel instance responsible for shoveling data from or
                    to the refered queue.

        Raises:
            QueuePoolError: An error occurred retrieving the object.
        """

        if not self.hasQueue(name):
            raise QueuePoolError("There is no queue registered with name '%s'" % (name))

        for connection, instance in self.connections.items():
            if name in connection:
                return instance

        raise QueuePoolError("Queue '%s' is not connected." % (name))

    def getConnectedQueue(self, name):
        """
        Returns the name of the queue to which the refered queue is connected.

        Args:
            name (str): The name of the queue

        Returns:
            str: The name of the queue

        Raises:
            QueuepoolError: Queue is not connected
        """

        for connection in self.connections:
            if name in connection:
                return connection[connection.index(name) - 1]
        raise QueuePoolError("Queue '%s' is not connected." % (name))

    def getQueue(self, name):
        """
        Get the queue instance

        Args:
            name (str): The queue name

        Returns:
            Queue: A queue object instance.

        Raises:
            QueuePoolError: In case the queue doesn't exist
        """

        if name in self.queues:
            return self.queues[name]
        else:
            raise QueuePoolError("There is no such queue '%s'" % (name))

    def hasQueue(self, name):
        """
        Returns True if the queue has been registered, otherwise False

        Args:
            name (str): The name of the queue

        Returns:
            bool: Returns True in case the queue has been registered.
        """

        return name in self.queues

    def isConnected(self, name):
        """
        Validates whether the queue is connected.

        Args:
            name (str): The name of the queue

        Returns:
            bool: Returns True if the queue is connected otherwise False

        Raises:
            n/a
        """

        if not self.hasQueue(name):
            raise QueuePoolError("There is no queue registered with name '%s'" % (name))
        else:
            for connection in self.connections:
                if name in connection:
                    return True

            return False

    def join(self):
        """
        Joins all queues

        Args:
            n/a

        Returns:
            n/a

        Raises:
            n/a
        """

        for queue in self.queues:
            queue.join()

    def listQueues(self):
        """
        returns the list of queue names and instances from the queuepool.

        Args:
            None

        Yields:
            str: The name of the queue
            Queue: a ``Queue`` instance

        """

        for name, instance in self.queues.items():
            yield name, instance

    def registerQueue(self, name, instance):
        """
        Registers a new queue instance to the queuepool

        Args:
            name (str): The name of the queue
            instance (object): A Queue instance

        Returns:
            None

        Raises:
            None
        """

        if instance in self.queues.values():
            raise QueuePoolError("This queue instance has already been registered.")

        if not self.hasQueue(name):
            instance.enableFallThrough()
            self.queues[name] = instance
        else:
            raise QueuePoolError(
                "There is already a queue registered named '%s'." % (name)
            )

    def __stats(self):

        while True:
            for queue, instance in self.listQueues():
                print(queue, instance.size())
            sleep(1)


class NameSpace(object):
    pass


class QueuePoolWrapper(object):
    """
    A wrapper class for QueuePool to pass to Actors so they only have access
    to a limited set of QueuePool methods and objects.
    """

    DEFAULT_QUEUES = ["_logs", "_metrics", "_failed", "_success"]

    def __init__(self, module_name, queue_pool):
        """
        Convenience wrapper for Wishbone Actor objects around `QueuePool`.

        Args:
            module_name (str): The name of the module to pass this instance.
            queue_pool (QueuePool): The QueuePool instance.
        """
        self._module_name = module_name
        self._queue_pool = queue_pool
        self.queue = NameSpace()
        self.__registerExistingQueues()

    def createQueue(self, name, instance=None):

        if name.startswith("_"):
            raise QueuePoolError(
                "Only system queue names can start with underscore. '%s'" % (name)
            )

        if instance is None:
            instance = MemoryQueue()

        self._queue_pool.registerQueue("%s.%s" % (self._module_name, name), instance)
        setattr(
            self.queue,
            name,
            self._queue_pool.getQueue("%s.%s" % (self._module_name, name)),
        )

    def createSystemQueue(self, name, instance=None):

        self._queue_pool.registerQueue("%s.%s" % (self._module_name, name), instance)

        if instance is None:
            instance = MemoryQueue()

        setattr(
            self.queue,
            name,
            self._queue_pool.getQueue("%s.%s" % (self._module_name, name)),
        )

    def getQueue(self, name):

        return self._queue_pool.getQueue("%s.%s" % (self._module_name, name))

    get = getQueue

    def hasQueue(self, name):

        return self._queue_pool.hasQueue("%s.%s" % (self._module_name, name))

    def listQueues(self, default=False, names=True):
        for name, instance in self._queue_pool.listQueues():
            module_name, queue_name = name.split(".")
            if module_name == self._module_name:
                if not default and queue_name in self.DEFAULT_QUEUES:
                    continue
                else:
                    if names:
                        yield queue_name
                    else:
                        yield instance

    def __registerExistingQueues(self):

        for name, instance in self._queue_pool.listQueues():
            module_name, queue_name = name.split(".")
            if module_name == self._module_name:
                setattr(self.queue, queue_name, instance)
