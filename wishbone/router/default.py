#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  default.py
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

from wishbone.actorconfig import ActorConfig
from wishbone.error import ModuleInitFailure, NoSuchModule
from wishbone.error import QueueConnected
from wishbone.componentmanager import ComponentManager
from gevent import event, sleep, spawn
from gevent import pywsgi
from .graphcontent import GRAPHCONTENT
from .graphcontent import VisJSData
from types import SimpleNamespace


class ModulePool():

    def __init__(self):

        self.module = SimpleNamespace()

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

    def hasModule(self, name):
        '''
        Checks whether the module pool has this module.


        Args:
            name (str): The name of the module instance.

        Returns
            bool: True if module exists False if not.
        '''

        return name in self.module.__dict__.keys()


class Default(object):

    '''
    The default Wishbone router.

    A Wishbone router is responsible for organising the event flow between
    modules.

    Args:
        config (EasyDict): The router setup configuration.
        size (int): The size of all queues.
        frequency (int)(1): The frequency at which metrics are produced.
        identification (wishbone): A string identifying this instance in logging.
    '''

    def __init__(self, config=None, size=100, frequency=10, identification="wishbone", graph=False, graph_include_sys=False):

        self.component_manager = ComponentManager()
        self.config = config
        self.size = size
        self.frequency = frequency
        self.identification = identification
        self.graph = graph
        self.graph_include_sys = graph_include_sys

        self.module_pool = ModulePool()
        self.__block = event.Event()
        self.__block.clear()

        self.__connections = {
        }

    def block(self):
        '''Blocks until stop() is called and the shutdown process ended.'''

        self.__block.wait()

    def connectQueue(self, source, destination):
        '''Connects one queue to the other.

        For convenience, the syntax of the queues is <modulename>.<queuename>
        For example:

            stdout.inbox

        This type of router actually replaces the destination queue with the source
        queue.

        Args:
            source (str): The source queue in <module.queue_name> syntax
            destination (str): The destination queue in <module.queue_name> syntax
        '''

        (source_module, source_queue) = source.split('.')
        (destination_module, destination_queue) = destination.split('.')

        if not self.module_pool.hasModule(source_module):
            raise NoSuchModule("Module instance %s does not exist." % (source_module))

        if not self.module_pool.hasModule(destination_module):
            raise NoSuchModule("Module instance %s does not exist." % (destination_module))

        result = self.__isConnectedTo(source)
        if result is not None:
            raise QueueConnected("Queue %s is already connected to %s." % (source, result))

        result = self.__isConnectedTo(destination)
        if result is not None:
            raise QueueConnected("Queue %s is already connected to %s." % (destination, result))

        self.__connections[source] = destination

        source_module_instance = self.module_pool.getModule(source_module)
        if not source_module_instance.pool.hasQueue(source_queue):
            source_module_instance.pool.createSystemQueue(source_queue)
            source_module_instance.logging.debug("Module instance '%s' has no queue '%s' so auto created." % (source_module, source_queue))

        destination_module_instance = self.module_pool.getModule(destination_module)
        if not destination_module_instance.pool.hasQueue(destination_queue):
            destination_module_instance.pool.createSystemQueue(destination_queue)
            destination_module_instance.logging.debug("Module instance '%s' has no queue '%s' so auto created." % (destination_module, destination_queue))

        setattr(
            destination_module_instance.pool.queue,
            destination_queue,
            source_module_instance.pool.getQueue(
                source_queue
            )
        )

        source_module_instance.pool.getQueue(source_queue).disableFallThrough()
        source_module_instance.logging.debug("Connected queue %s to %s" % (source, destination))

    def getChildren(self, module):
        '''
        Returns all the connected child modules

        Args:
            module (str): The name of the module.

        Returns:
            list: A list of module names.
        '''

        children = []

        def travel(m):
            for connection in self.__connections:
                if connection.split('.')[0] == m:
                    child = self.__connections[connection].split('.')[0]
                    if child in children:
                        continue
                    else:
                        children.append(child)
                        travel(child)

        travel(module)
        return children

    def registerModule(self, module, actor_config, arguments={}):
        '''Initializes the wishbone module ``module``.

        Args:
            module (str): A Wishbone module component name.
            actor_config (ActorConfig): The module's actor configuration
            arguments (dict): The parameters to initialize the module.
        '''

        try:
            m = self.component_manager.getComponentByName(module)
            setattr(self.module_pool.module, actor_config.name, m(actor_config, **arguments))
        except Exception as err:
            raise ModuleInitFailure("Problem loading module '%s'.  Reason: %s" % (actor_config.name, err))

    def stop(self):
        '''Stops all running modules.'''

        for module in self.module_pool.list():
            if module.name not in list(self.getChildren("_logs")) + ["_logs"] and not module.stopped:
                module.stop()

        while not self.__logsEmpty():
            sleep(0.1)

        self.__running = False
        self.__block.set()

    def start(self):
        '''Starts all registered modules.'''

        if self.config is not None:
            self.__initConfig()

        if self.graph:
            self.graph = GraphWebserver(self.config, self.module_pool, self.__block, self.graph_include_sys)
            self.graph.start()

        for module in self.module_pool.list():
            module.start()

    def __initConfig(self):
        '''Setup all modules and routes.'''

        protocols = {}
        for name, instance in list(self.config.protocols.items()):
            protocols[name] = self.component_manager.getComponentByName(instance.protocol)(**instance.arguments)

        template_functions = {}
        for name, instance in list(self.config.template_functions.items()):
            template_functions[name] = self.component_manager.getComponentByName(instance.function)(**instance.arguments)

        module_functions = {}
        for name, instance in list(self.config.module_functions.items()):
            module_functions[name] = self.component_manager.getComponentByName(instance.function)(**instance.arguments)

        for name, instance in list(self.config.modules.items()):
            mod_func = {}
            for queue, queue_functions in list(instance.functions.items()):
                mod_func[queue] = []
                for queue_function in queue_functions:
                    if queue_function in module_functions:
                        mod_func[queue].append(module_functions[queue_function])

            if instance.protocol is None:
                protocol = None
            elif instance.protocol not in protocols:
                raise ModuleInitFailure("Protocol %s referenced but not available." % (instance.protocol))
            else:
                protocol = protocols[instance.protocol]

            actor_config = ActorConfig(
                name=name,
                size=self.size,
                frequency=self.frequency,
                template_functions=template_functions,
                description=instance.description,
                module_functions=mod_func,
                identification=self.identification,
                protocol=protocol,
                io_event=instance.event
            )

            self.registerModule(
                instance.module,
                actor_config,
                instance.arguments
            )

        self.__setupConnections()

    def __isConnectedTo(self, queue):
        '''
        Returns the module.queue ``queue`` is connected to.

        Args:
            queue (str): The name of the queue in ``module.queue`` format.

        Returns
            str/None: The name of the queue which is connected.
        '''

        inverse = {v: k for k, v in self.__connections.items()}

        if queue in self.__connections:
            return self.__connections[queue]
        elif queue in inverse:
            return inverse[queue]
        else:
            return None

    def __logsEmpty(self):
        '''Checks each module whether any logs have stayed behind.'''

        for module in self.module_pool.list():
            if not module.pool.queue._logs.size() == 0:
                return False
        else:
            return True

    def __setupConnections(self):
        '''Setup all connections as defined by configuration_manager'''

        for route in self.config.routingtable:
            self.connectQueue("%s.%s" % (route.source_module, route.source_queue), "%s.%s" % (route.destination_module, route.destination_queue))


class GraphWebserver():

    def __init__(self, config, module_pool, block, include_sys):
        self.config = config
        self.module_pool = module_pool
        self.block = block
        self.include_sys = include_sys
        self.js_data = VisJSData()

        for c in self.config["routingtable"]:
            if not self.include_sys and any([
                    c.source_module.startswith('_'),
                    c.destination_module.startswith('_'),
                    c.source_queue.startswith('_'),
                    c.destination_queue.startswith('_')]):
                continue
            else:
                self.js_data.addModule(instance_name=c.source_module,
                                       module_name=self.config["modules"][c.source_module]["module"],
                                       description=self.module_pool.getModule(c.source_module).description)

                self.js_data.addModule(instance_name=c.destination_module,
                                       module_name=self.config["modules"][c.destination_module]["module"],
                                       description=self.module_pool.getModule(c.destination_module).description)

                self.js_data.addQueue(c.source_module, c.source_queue)
                self.js_data.addQueue(c.destination_module, c.destination_queue)
                self.js_data.addEdge("%s.%s" % (c.source_module, c.source_queue), "%s.%s" % (c.destination_module, c.destination_queue))

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

    def application(self, env, start_response):
        if env['PATH_INFO'] == '/':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return[str.encode(GRAPHCONTENT % (self.js_data.dumpString()[0], self.js_data.dumpString()[1]))]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b'<h1>Not Found</h1>']

    def setupWebserver(self):

        pywsgi.WSGIServer(('', 8088), self.application, log=None, error_log=None).serve_forever()
