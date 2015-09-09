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
from gevent import signal, event, sleep, spawn
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
        self.config = router_config
        self.module_manager = module_manager
        self.size = size
        self.frequency = frequency
        self.identification = identification
        self.stdout_logging = stdout_logging
        self.process = process

        self.module_pool = ModulePool()

        self.__running = False
        self.__block = event.Event()
        self.__block.clear()

        signal.signal(2, self.initiateStop)
        signal.signal(15, self.__noop)

        self.initiate_stop = event.Event()
        self.initiate_stop.clear()
        spawn(self.stop)

    def block(self):
        '''Blocks until stop() is called.'''
        self.__block.wait()

    def getChildren(self, module):
        children = []

        def lookupChildren(module, children):
            for module in self.module_pool.getModule(module).getChildren():
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

    def initiateStop(self, *args, **kwargs):

        self.initiate_stop.set()

    def stop(self):
        '''Stops all modules.'''

        self.initiate_stop.wait()
        for module in self.module_pool.list():
            if module.name not in self.getChildren("wishbone_logs") + ["wishbone_logs"] and not module.stopped:
                module.stop()

        while not self.__logsEmpty():
            sleep(0.1)

        # This gives an error when starting in background, no idea why
        # self.module_pool.module.wishbone_logs.stop()

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

        source = self.module_pool.getModule(source_module)
        destination = self.module_pool.getModule(destination_module)

        source.connect(source_queue, destination, destination_queue)

    def __initConfig(self):
        '''Setup all modules and routes.'''

        lookup_modules = {}
        for name, config in self.config.lookups.iteritems():
            lookup_modules[name] = self.__registerLookupModule(config.module, **config.get('arguments', {}))

        self.__registerModule(Funnel, ActorConfig("wishbone_metrics", self.size, self.frequency, self.config.lookups))
        self.__registerModule(Funnel, ActorConfig("wishbone_logs", self.size, self.frequency, self.config.lookups))

        for name, instance in self.config.modules.iteritems():
            if name in ["metrics", "logs"]:
                raise ModuleInitFailure('"%s" is a reserved name you cannot use as a module instance name.' % (name))
            pmodule = self.module_manager.getModuleByName(instance.module)
            actor_config = ActorConfig(name, self.size, self.frequency, lookup_modules)
            self.__registerModule(pmodule, actor_config, instance.get("arguments", {}))

            self.module_pool.getModule(name).connect("metrics", self.module_pool.module.wishbone_metrics, name)
            self.module_pool.getModule(name).connect("logs", self.module_pool.module.wishbone_logs, name)

        self.__setupConnections()

        if self.stdout_logging:
            self.__setupSTDOUTLogging()
        else:
            self.__setupSyslogLogging()

    def __logsEmpty(self):
        '''Checks each module whether any logs have stayed behind.'''

        for module in self.module_pool.list():
            if not module.pool.queue.logs.size() == 0:
                return False
        else:
            return True

    def __noop(self, *args, **kwargs):
        pass

    def __registerLookupModule(self, name, **kwargs):

        base = ".".join(name.split('.')[0:-1])
        function = name.split('.')[-1]
        m = importlib.import_module(base)
        return getattr(m, function)(**kwargs)

    def __registerModule(self, module, actor_config, arguments={}):
        '''Initializes the wishbone module module.'''

        try:
            setattr(self.module_pool.module, actor_config.name, module(actor_config, **arguments))
        except Exception as err:
            raise ModuleInitFailure("Problem loading module %s.  Reason: %s" % (actor_config.name, err))

    def __setupConnections(self):
        '''Setup all connections as defined by configuration_manager'''

        for route in self.config.routingtable:
            self.__connect("%s.%s" % (route.source_module, route.source_queue), "%s.%s" % (route.destination_module, route.destination_queue))

    def __setupSTDOUTLogging(self):

        log_stdout = self.module_manager.getModuleByName("wishbone.output.stdout")
        stdout_actor_config = ActorConfig("log_stdout", self.size, self.frequency, self.config.lookups)

        log_human = self.module_manager.getModuleByName("wishbone.encode.humanlogformat")
        human_actor_config = ActorConfig("log_format", self.size, self.frequency, self.config.lookups)
        self.__registerModule(log_stdout, stdout_actor_config)
        self.__registerModule(log_human, human_actor_config)
        try:
            self.__connect("wishbone_logs.outbox", "log_format.inbox")
            self.__connect("log_format.outbox", "log_stdout.inbox")
        except QueueConnected:
            pass

    def __setupSyslogLogging(self):

        actor_config = ActorConfig("log_syslog", self.size, self.frequency, self.config.lookups)
        log_syslog = self.module_manager.getModuleByName("wishbone.output.syslog")
        self.__registerModule(log_syslog, actor_config)
        self.__connect("wishbone_logs.outbox", "log_syslog.inbox")

    def __start(self):

        self.__initConfig()
        self.__running = True

        for module in self.module_pool.list():
            module.start()

        self.block()

