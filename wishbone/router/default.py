#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  default.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
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
from wishbone.error import ModuleInitFailure, NoSuchModule, QueueConnected
from gevent import signal, event, sleep
import multiprocessing
import importlib


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

        - router_config(obj)            : The router setup configuration.

        - module_manager(obj)           : A Wishbone ModuleManager object instance.

        - size(int)(100)                : The size of all queues.

        - frequency(int)(1)             : The frequency at which metrics are produced.

        - identification                : A string identifying this instance in logging.

        - stdout_logging(bool)(True)    : When True all logs are written to STDOUT.

        - background(bool)(False)       : When True, sends the router to background in a
                                          separate process.


    '''

    def __init__(self, router_config, module_manager, size=100, frequency=1, identification="wishbone", stdout_logging=True, process=False):

        if process:
            multiprocessing.Process.__init__(self)
            self.daemon = True
        # self.configuration_manager = configuration_manager
        self.config = router_config
        self.module_manager = module_manager
        self.size = size
        self.frequency = frequency
        self.identification = identification
        self.stdout_logging = stdout_logging
        self.process = process

        self.pool = ModulePool()

        self.__running = False
        self.__block = event.Event()
        self.__block.clear()

        signal(2, self.stop)
        signal(15, self.__noop)

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

        if self.process:
            self.run = self.__start
            multiprocessing.Process.start(self)
            return self
        else:
            self.__start()

    def stop(self):
        '''Stops all input modules.'''

        for module in self.pool.list():
            if module.name not in self.getChildren("wishbone_logs"):
                module.stop()

        while not self.__logsEmpty():
            sleep(0.5)

        # This gives an error when starting in background, no idea why
        # self.pool.module.wishbone_logs.stop()

        self.__running = False
        self.__block.set()

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

        lookup_modules = {}
        for name, config in self.config.lookup.iteritems():
            lookup_modules[name] = self.__registerLookupModule(config.module, config.get('arguments', {}))

        for name, instance in self.config.module.iteritems():
            pmodule = self.module_manager.getModuleByName(instance.module)
            actor_config = ActorConfig(name, self.size, self.frequency, lookup_modules)
            self.__registerModule(pmodule, actor_config, instance.get("arguments", {}))

        self.__setupMetricConnections()
        self.__setupLogConnections()
        self.__setupConnections()

        if self.stdout_logging:
            self.__setupSTDOUTLogging()
        else:
            self.__setupSyslogLogging()

    def __logsEmpty(self):
        '''Checks each module whether any logs have stayed behind.'''

        for module in self.pool.list():
            if not module.pool.queue.logs.size() == 0:
                return False
        else:
            return True

    def __noop(self):
        pass

    def __registerLookupModule(self, name, arguments):

        base = ".".join(name.split('.')[0:-1])
        function = name.split('.')[-1]
        m = importlib.import_module(base)
        return getattr(m, function)(**arguments)

    def __registerModule(self, module, actor_config, arguments={}):
        '''Initializes the wishbone module module.'''

        # try:
        setattr(self.pool.module, actor_config.name, module(actor_config, **arguments))
        # except Exception as err:
        #     raise ModuleInitFailure("Problem loading module %s.  Reason: %s" % (actor_config.name, err))

    def __setupConnections(self):
        '''Setup all connections as defined by configuration_manager'''

        for route in self.config.routingtable:
            self.__connect("%s.%s" % (route.source_module, route.source_queue), "%s.%s" % (route.destination_module, route.destination_queue))

    def __setupLogConnections(self):
        '''Connect all log queues to a Funnel module'''

        actor_config = ActorConfig("wishbone_logs", self.size, self.frequency, self.config.lookup)
        self.__registerModule(Funnel, actor_config)
        for module in self.pool.list():
            module.connect("logs", self.pool.module.wishbone_logs, module.name)

    def __setupMetricConnections(self):
        '''Connects all metric queues to a Funnel module'''

        actor_config = ActorConfig("wishbone_metrics", self.size, self.frequency, self.config.lookup)
        self.__registerModule(Funnel, actor_config)
        for module in self.pool.list():
            module.connect("metrics", self.pool.module.wishbone_metrics, module.name)

    def __setupSTDOUTLogging(self):

        log_stdout = self.module_manager.getModuleByName("wishbone.output.stdout")
        stdout_actor_config = ActorConfig("log_stdout", self.size, self.frequency, self.config.lookup)

        log_human = self.module_manager.getModuleByName("wishbone.encode.humanlogformat")
        human_actor_config = ActorConfig("log_format", self.size, self.frequency, self.config.lookup)

        self.__registerModule(log_stdout, stdout_actor_config)
        self.__registerModule(log_human, human_actor_config)
        try:
            self.__connect("wishbone_logs.outbox", "log_format.inbox")
            self.__connect("log_format.outbox", "log_stdout.inbox")
        except QueueConnected:
            pass

    def __setupSyslogLogging(self):

        actor_config = ActorConfig("log_syslog", self.size, self.frequency, self.config.lookup)
        log_syslog = self.module_manager.getModuleByName("wishbone.output.syslog")
        self.__registerModule(log_syslog, actor_config)
        self.__connect("wishbone_logs.outbox", "log_syslog.inbox")

    def __start(self):

        self.__initConfig()
        self.__running = True

        for module in self.pool.list():
            module.start()

        self.block()

