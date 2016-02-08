#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  default.py
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

from wishbone.actor import ActorConfig
from wishbone.error import ModuleInitFailure, NoSuchModule
from gevent import signal, event, sleep, spawn
import multiprocessing
import importlib
from gevent import pywsgi
import json
from .graphcontent import GRAPHCONTENT
from .graphcontent import VisJSData


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

    def __init__(self, router_config, module_manager, size=100, frequency=1, identification="wishbone", stdout_logging=True, process=False, graph=False, graph_include_sys=False):

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
        self.graph = graph
        self.graph_include_sys = graph_include_sys

        self.module_pool = ModulePool()

        self.__running = False
        self.__block = event.Event()
        self.__block.clear()

        signal(2, self.initiateStop)
        signal(15, self.__noop)

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
            if module.name not in self.getChildren("_logs") + ["_logs"] and not module.stopped:
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

        for name, instance in self.config.lookups.iteritems():
            lookup_modules[name] = self.__registerLookupModule(instance.module, **instance.arguments)

        for name, instance in self.config.modules.iteritems():
            pmodule = self.module_manager.getModuleByName(instance.module)

            if instance.description == "":
                instance.description = pmodule.__doc__.split("\n")[0].replace('*', '')

            actor_config = ActorConfig(name, self.size, self.frequency, lookup_modules, instance.description)

            self.__registerModule(pmodule, actor_config, instance.arguments)

        self.__setupConnections()

    def __logsEmpty(self):
        '''Checks each module whether any logs have stayed behind.'''

        for module in self.module_pool.list():
            if not module.pool.queue.logs.size() == 0:
                return False
        else:
            return True

    def __noop(self, *args, **kwargs):
        pass

    def __registerLookupModule(self, module, **kwargs):

        base = ".".join(module.split('.')[0:-1])
        function = module.split('.')[-1]
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

    def __start(self):

        self.__initConfig()
        self.__running = True

        if self.graph:
            self.graph = GraphWebserver(self.config, self.module_pool, self.__block, self.graph_include_sys)
            self.graph.start()

        for module in self.module_pool.list():
            module.start()

        self.block()


class GraphWebserver():

    def __init__(self, config, module_pool, block, include_sys):
        self.config = config
        self.module_pool = module_pool
        self.block = block
        self.js_data = VisJSData()

        for c in self.config["routingtable"]:
            if self.__include(include_sys, self.config["modules"][c.source_module]["context"], self.config["modules"][c.destination_module]["context"]):
                self.js_data.addModule(instance_name=c.source_module,
                                       module_name=self.config["modules"][c.source_module]["module"],
                                       description=self.module_pool.getModule(c.source_module).description)

                self.js_data.addModule(instance_name=c.destination_module,
                                       module_name=self.config["modules"][c.destination_module]["module"],
                                       description=self.module_pool.getModule(c.destination_module).description)

                self.js_data.addQueue(c.source_module, c.source_queue)
                self.js_data.addQueue(c.destination_module, c.destination_queue)
                self.js_data.addEdge("%s.%s" % (c.source_module, c.source_queue), "%s.%s" % (c.destination_module, c.destination_queue))

    def __include(self, include_sys, source_module_context, destination_module_context):

        if include_sys:
            return True
        elif source_module_context not in ["_logs", "_metrics"] and destination_module_context not in ["_logs", "_metrics"]:
            return True
        else:
            return False

    def start(self):

        print "#####################################################"
        print "#                                                   #"
        print "# Caution: Started webserver on port 8088           #"
        print "#                                                   #"
        print "#####################################################"
        spawn(self.setupWebserver)

    def stop(self):
        pass

    def loop(self):

        return not self.block.isSet()

    def getMetrics(self):

        def getConnectedModuleQueue(m, q):
            for c in self.config["routingtable"]:
                if c.source_module == m and c.source_queue == q:
                    return (c.destination_module, c.destination_queue)
            return (None, None)

        d = {"module": {}}
        for module in self.module_pool.list():
            d["module"][module.name] = {}
            for queue in module.pool.listQueues(names=True):
                d["module"][module.name]["queue"] = {queue: {"metrics": module.pool.getQueue(queue).stats()}}
                (dest_mod, dest_q) = getConnectedModuleQueue(module.name, queue)
                if dest_mod is not None and dest_q is not None:
                    d["module"][module.name]["queue"] = {queue: {"connection": {"module": dest_mod, "queue": dest_q}}}
        return json.dumps(d)

    def application(self, env, start_response):
        if env['PATH_INFO'] == '/':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return[GRAPHCONTENT % (self.js_data.dumpString()[0], self.js_data.dumpString()[1])]
        elif env['PATH_INFO'] == '/metrics':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return[self.getMetrics()]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b'<h1>Not Found</h1>']

    def setupWebserver(self):

        pywsgi.WSGIServer(('', 8088), self.application, log=None, error_log=None).serve_forever()
