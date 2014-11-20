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

from wishbone.actor import ActorConfig
from wishbone.module import Funnel
from wishbone.error import ModuleInitFailure, NoSuchModule
from gevent import signal, event, sleep
import multiprocessing


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


class Default(multiprocessing.Process):

    '''The default Wishbone router.

    Holds all Wishbone modules and connections.

    Arguments:

        - configuration_manager(obj)    : A Wishbone ConfigManager object instance.

        - module_manager(obj)           : A Wishbone ModuleManager object instance.

        - size(int)(100)                : The size of all queues.

        - frequency(int)(1)             : The frequency at which metrics are produced.

        - identification                : A string identifying this instance in logging.

        - stdout_logging(bool)(True)    : When True all logs are written to STDOUT.

        - background(bool)(False)       : When True, sends the router to background in a
                                          separate process.


    '''

    def __init__(self, configuration_manager, module_manager, size=100, frequency=1, identification="wishbone", stdout_logging=True, background=False):

        if background:
            signal(15, self.stop)
            multiprocessing.Process.__init__(self)

        self.configuration_manager = configuration_manager
        self.module_manager = module_manager
        self.size = size
        self.frequency = frequency
        self.identification = identification
        self.stdout_logging = stdout_logging
        self.background = background

        self.pool = ModulePool()

        self.__running = False
        self.__block = event.Event()
        self.__block.clear()

    def block(self):
        '''Blocks until stop() is called.'''
        self.__block.wait()

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

    def isRunning(self):
        return self.__running

    def start(self):
        '''Starts all registered modules.'''

        if self.background:
            self.run = self.__start
            multiprocessing.Process.start(self)
        else:
            self.__start()

    def stop(self):
        '''Stops all input modules.'''

        for module in self.pool.list():
            if module.name not in self.getChildren("logs_funnel"):
                module.stop()

        while not self.__logsEmpty():
            sleep(0.5)

        # This gives an error when starting in background, no idea why
        # self.pool.module.logs_funnel.stop()

        self.__running = False
        self.__block.set()

    def __logsEmpty(self):
        '''Checks each module whether any logs have stayed behind.'''

        for module in self.pool.list():
            if not module.pool.queue.logs.size() == 0:
                return False
        else:
            return True

    def __connect(self, source, destination):
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

    def __initConfig(self):
        '''Setup all modules and routes.'''

        for module in self.configuration_manager.modules:
            arguments = {x: getattr(module.arguments, x) for x in module.arguments}
            pmodule = self.module_manager.getModuleByName(module.module)
            self.__registerModule(pmodule, module.instance, **arguments)

        self.__setupConnections()
        self.__setupMetricConnections()
        self.__setupLogConnections()

        if self.stdout_logging:
            self.__setupSTDOUTLogging()

    def __registerModule(self, module, name, *args, **kwargs):
        '''Initializes the mdoule using the provided <args> and <kwargs>
        arguments.'''

        try:
            actor_config = ActorConfig(name, self.size, self.frequency)
            setattr(self.pool.module, name, module(actor_config, *args, **kwargs))
        except Exception as err:
            raise ModuleInitFailure(err)

    def __setupConnections(self):
        '''Setup all connections as defined by configuration_manager'''

        for module in self.configuration_manager.modules:
            for route in module.outgoing:
                self.__connect("%s.%s" % (route.source_module, route.source_queue), "%s.%s" % (route.destination_module, route.destination_queue))

    def __setupLogConnections(self):
        '''Connect all log queues to a Funnel module'''

        self.__registerModule(Funnel, "logs_funnel")
        for module in self.pool.list():
            module.connect("logs", self.pool.module.logs_funnel, module.name)

    def __setupMetricConnections(self):
        '''Connects all metric queues to a Funnel module'''

        self.__registerModule(Funnel, "metrics_funnel")
        for module in self.pool.list():
            module.connect("metrics", self.pool.module.metrics_funnel, module.name)

    def __setupSTDOUTLogging(self):

        log_stdout = self.module_manager.getModuleByName("wishbone.output.stdout")
        log_human = self.module_manager.getModuleByName("wishbone.encode.humanlogformat")
        self.__registerModule(log_stdout, "log_stdout")
        self.__registerModule(log_human, "log_format", ident=self.identification)
        self.__connect("logs_funnel.outbox", "log_format.inbox")
        self.__connect("log_format.outbox", "log_stdout.inbox")

    def __start(self):

        self.__initConfig()
        self.__running = True

        for module in self.pool.list():
            module.start()

        self.block()


