#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  default.py
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

from wishbone.module import Funnel
from wishbone.error import ModuleInitFailure, NoSuchModule
from gevent import signal, event


class Container():
    pass


class ModulePool():

    def __init__(self):

        self.module = Container()

    def list(self):
        '''Returns a generator returning all module instances.'''

        for m in self.module.__dict__.keys():
            yield self.module.__dict__[m]

    def getModule(self, name):
        '''Returns a module instance'''

        try:
            return getattr(self.module, name)
        except AttributeError:
            raise NoSuchModule("Could not find module %s" % name)


class Default():

    def __init__(self, size=100, frequency=1):
        signal(2, self.stop)
        signal(15, self.stop)
        self.pool = ModulePool()
        self.size = size
        self.frequency = frequency
        self.registerModule(Funnel, "metrics_funnel")
        self.registerModule(Funnel, "logs_funnel")
        self.__running = False
        self.__block = event.Event()
        self.__block.clear()

    def block(self):
        '''Blocks until stop() is called.'''
        self.__block.wait()

    def connect(self, source, destination):
        '''Connects one queue to the other.

        For convenience, the syntax of the queues is <modulename>.<queuename>
        For example:

            stdout.inbox
        '''

        (source_module, source_queue) = source.split('.')
        (destination_module, destination_queue) = destination.split('.')

        source = self.pool.getModule(source_module)
        destination = self.pool.getModule(destination_module)

        source.connect(source_queue, destination, destination_queue)

    def getChildren(self, module):
        children = []

        def lookupChildren(module, children):
            for module in self.pool.getModule(module).getChildren():
                name = module.split(".")[0]
                if name not in children:
                    children.append(name)
                    lookupChildren(name, children)

        lookupChildren(module, children)
        return children

    def registerModule(self, module, name, *args, **kwargs):
        '''Initializes the mdoule using the provided <args> and <kwargs>
        arguments.'''

        try:
            setattr(self.pool.module, name, module(name, self.size, self.frequency, *args, **kwargs))
        except Exception as err:
            raise ModuleInitFailure(err)

    def isRunning(self):
        return self.__running

    def setupMetricConnections(self):
        '''Connects all metric queues to a Funnel module'''

        for module in self.pool.list():
            module.connect("metrics", self.pool.module.metrics_funnel, module.name)

    def setupLogConnections(self):
        '''Connect all log queues to a Funnel module'''

        for module in self.pool.list():
            module.connect("logs", self.pool.module.logs_funnel, module.name)

    def start(self):
        '''Starts all registered modules.'''
        self.__running = True
        self.setupMetricConnections()
        self.setupLogConnections()

        for module in self.pool.list():
            module.start()

    def stop(self):
        '''Stops all input modules.'''

        for module in self.pool.list():
            if module.name not in self.getChildren("logs_funnel"):
                module.stop()

        self.pool.module.logs_funnel.stop()
        self.__running = False
        self.__block.set()
