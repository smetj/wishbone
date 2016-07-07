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

from gevent import monkey; monkey.patch_os()
from gevent.signal import signal
from wishbone.actor import ActorConfig
from wishbone.error import ModuleInitFailure, NoSuchModule, FunctionInitFailure
from wishbone import ModuleManager
from gevent import event, sleep, spawn
import multiprocessing
from gevent import pywsgi
import json
from .graphcontent import GRAPHCONTENT
from .graphcontent import VisJSData
from pkg_resources import iter_entry_points


class Container():
    pass


class ModulePool():

    def __init__(self):

        self.module = Container()

    def list(self):
        '''Returns a generator returning all module instances.'''

        for m in list(self.module.__dict__.keys()):
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

        - size(int)(100)                : The size of all queues.

        - frequency(int)(1)             : The frequency at which metrics are produced.

        - identification                : A string identifying this instance in logging.

        - background(bool)(False)       : When True, sends the router to background in a
                                          separate process.


    '''

<<<<<<< Updated upstream
    def __init__(self, router_config, size=100, frequency=1, identification="wishbone", stdout_logging=True, process=False, graph=False, graph_include_sys=False):
=======
    def __init__(self, router_config=None, size=100, frequency=1, identification="wishbone", process=False, graph=False, graph_include_sys=False):
>>>>>>> Stashed changes

        if process:
            multiprocessing.Process.__init__(self)
            self.daemon = True

        self.module_manager = ModuleManager()
        self.router_config = router_config
        self.size = size
        self.frequency = frequency
        self.identification = identification
        self.process = process
        self.graph = graph
        self.graph_include_sys = graph_include_sys

        self.module_pool = ModulePool()
        self.__block = True

    def block(self):
        '''Blocks until stop() is called.'''

<<<<<<< Updated upstream
        signal(2, self.initiateStop)
        signal(15, self.__noop)
=======
        while self.__block:
            sleep(0.5)
>>>>>>> Stashed changes

    def connectQueue(self, source, destination):
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

    def registerModule(self, module, actor_config, arguments={}):
        '''Initializes the wishbone module module.'''

        try:
            setattr(self.module_pool.module, actor_config.name, module(actor_config, **arguments))
        except Exception as err:
            raise ModuleInitFailure("Problem loading module %s.  Reason: %s" % (actor_config.name, err))

    def start(self):
        '''Starts all registered modules.'''

        if self.process:
            self.run = self.__start
            multiprocessing.Process.start(self)
            return self
        else:
            self.__start()

    def stop(self):
        '''Stops all modules.'''

        for module in self.module_pool.list():
            if module.name not in self.getChildren("_logs") + ["_logs"] and not module.stopped:
                module.stop()

        while not self.__logsEmpty():
<<<<<<< Updated upstream
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
=======
            sleep(0.5)
        self.__block = False
>>>>>>> Stashed changes

    def __initConfig(self):
        '''Setup all modules and routes.'''

        lookup_modules = {}

        for name, instance in self.router_config.lookups.items():
            lookup_modules[name] = self.__registerLookupModule(instance.module, **instance.arguments)

        for name, instance in self.router_config.modules.items():
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

    def __registerLookupModule(self, module, **kwargs):

        for group in ["wishbone.lookup", "wishbone_contrib.lookup"]:
            for entry_point in iter_entry_points(group=group, name=None):
                if entry_point.module_name == module:
                    l = entry_point.load()(**kwargs)
                    if hasattr(l, "lookup"):
                        return l.lookup
                    else:
                        raise FunctionInitFailure("Lookup module '%s' does not seem to have a 'lookup' method" % (l.module_name))
        raise FunctionInitFailure("Lookup module '%s' does not exist." % (module))

<<<<<<< Updated upstream
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
=======
    def __setupConnections(self):
        '''Setup all connections as defined by configuration_manager'''

        for route in self.router_config.routingtable:
            self.connectQueue("%s.%s" % (route.source_module, route.source_queue), "%s.%s" % (route.destination_module, route.destination_queue))

    def __start(self):

        if self.router_config is not None:
            self.__initConfig()

>>>>>>> Stashed changes
        self.__running = True

        if self.graph:
            self.graph = GraphWebserver(self.router_config, self.module_pool, self.__block, self.graph_include_sys)
            self.graph.start()

        for module in self.module_pool.list():
            module.start()

        # If we run in multiprocessing.Process we should prevent from exiting
        if self.process:
            signal(10, self.__signalShutdown)
            self.block()

    def __signalShutdown(self, *args, **kwargs):

        self.stop()



class GraphWebserver():

    def __init__(self, config, module_pool, block, include_sys):
        self.router_config = config
        self.module_pool = module_pool
        self.block = block
        self.js_data = VisJSData()

        for c in self.router_config["routingtable"]:
            if self.__include(include_sys, self.router_config["modules"][c.source_module]["context"], self.router_config["modules"][c.destination_module]["context"]):
                self.js_data.addModule(instance_name=c.source_module,
                                       module_name=self.router_config["modules"][c.source_module]["module"],
                                       description=self.module_pool.getModule(c.source_module).description)

                self.js_data.addModule(instance_name=c.destination_module,
                                       module_name=self.router_config["modules"][c.destination_module]["module"],
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

        print("#####################################################")
        print("#                                                   #")
        print("# Caution: Started webserver on port 8088           #")
        print("#                                                   #")
        print("#####################################################")
        spawn(self.setupWebserver)

    def stop(self):
        pass

    def loop(self):

        return self.__block

    def getMetrics(self):

        def getConnectedModuleQueue(m, q):
            for c in self.router_config["routingtable"]:
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
