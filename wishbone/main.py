#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wishbone.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

import logging
import signal
from importlib import import_module
from pkg_resources import iter_entry_points
from gevent import spawn, sleep
from gevent.queue import Queue
from gevent.event import Event
from multiprocessing import current_process
from string import lstrip
from toolkit import Block
from sys import stderr
from time import time
from copy import deepcopy
from time import time

class Wishbone(Block):
    '''**The main class in which the Wishbone modules are registered and managed.**
    

    Parameters:

        * syslog (bool):                Enable/disable logging to syslog.
        * metrics (bool):               Enable/disable metrics.
        * metrics_interval (int):       The interval metrics need to be emitted.
        * metrics_dst (str):            The destination to write metrics to: [logging]
    '''

    def __init__(self, syslog=False):
        signal.signal(signal.SIGTERM, self.stop)
        self.logging = logging.getLogger( 'Wishbone' )
        self.logging.info("Wishbone version %s")
        Block.__init__(self)
        self.modules={}
        self.connectors={}
        self.metric_cache={"last_run":time(),"functions":{}}
        self.run=self.start

    def loadMetric(self, settings):
        '''Loads the metric module if required.'''
        if settings != {} and settings["enable"] == True:
            module=self.loadEntrypoint(settings["group"],settings["module"])
            self.metric_module=module(**settings["variables"])
            spawn(self.collectMetrics,settings["interval"])
        
    def loadModule(self, config, *args, **kwargs):
        '''Registers a Wishbone Module into the framework.  All modules used within Wishbone should be registered through this function.

        This function receives a tuple containing 3 values.  Any further args or kwargs are used to initialize the actual module you register.

        The config parameter should be a tuple of 3 strings:

            (group_name, class_name, name)

            * group:        The name of the entry point group under which the module is installed.  See module's setup.py
            * class:        The name of the class to initialize.
            * name:         The name under which the module should be initialized.

            *args and **kwargs are passed to the class which is initialized.

        self.modules is a dictionary containing all initialized modules.
        '''
        group_name = config[0]
        class_name = config[1]
        name = config[2]
        
        module = self.loadEntrypoint(group_name, class_name)
        self.modules[name]=module('Intance #%s:%s'%(self.getCurrentProcessName(),name), *args, **kwargs)
        try:
            #Do a couple of checks to see whether the loaded module is compliant.
            #todo: Flesh out checks.
            self.modules[name].inbox
            self.modules[name].outbox
        except:
            raise Exception("You might have to load QueueFunctions base class into this class.")
            
    def loadEntrypoint(self, group_name, class_name):
        try:
            loaded_module=None
            for module in iter_entry_points(group=group_name,name=class_name):
                loaded_module = module.load()
            if loaded_module==None:
                raise Exception("Group %s does not contain a %s class."%(group_name,class_name))
            else:
                return loaded_module
        except Exception as err:
            raise Exception("Problem loading %s.%s. Reason: %s" % ( group_name, class_name, err))

    def connect(self, source, destination):
        '''Creates a new background Greenthread which continuously consumes all messages from source into destination.

        Both source and destination should be strings.
        '''

        (src_class,src_queue)=source.split('.')
        (dst_class,dst_queue)=destination.split('.')
        src_queue = getattr(self.modules[src_class],src_queue)
        dst_queue = getattr(self.modules[dst_class],dst_queue)
        name = "%s->%s"%(source,destination)
        self.connectors[name] = Connector(name, src_queue, dst_queue)

    def start(self):
        '''Function which starts all registered Wishbone modules.

        Function which runs over all registered instances/modules and tries to execute the start() function in order to let that module start
        to consume the messages of its inbox and execute the consume function on each message.
        This function blocks from exiting.
        '''

        for module in self.modules:
            try:
                self.modules[module].start()
            except Exception as err:
                self.logging.warn("I was not able to start module %s. Reason: %s"%(module,err))

        for connector in self.connectors.keys():
            self.connectors[connector].start()

        while self.block():
            self.wait(0.1)

    def stop(self,a,b):
        '''Function which stops all registered Wishbone modules.

        Function which runs over all registered instances/modules and tries to execute its stop() function in order to stop that module.
        '''

        self.logging.info('Stop received.')
        for module in self.modules:
            self.modules[module].release()
            self.modules[module].shutdown()

            try:
                self.logging.debug('Waiting 1 second for module %s'%module.name)
                module.join(timeout=1)
            except:
                pass

        for connector in self.connectors:
            try:
                connector.join(timeout=1)
            except:
                pass

        #Now release ourselves
        self.release()

    def getCurrentProcessName(self):
        '''return the current process name withought the Process- part'''
        if current_process().name == 'Process-1':
            return '0'
        else:
            return str(current_process().name)

    def collectMetrics(self,interval):
        while self.block() == True:
            now = time()
            metrics={"functions":{},"connectors":{}}

            for module in self.modules:
                metrics["functions"][self.modules[module].name]=self.modules[module].metrics

            for connector in self.connectors:
                metrics["connectors"][connector] = self.connectors[connector].hits

            for instance in metrics["functions"]:
                for function in metrics["functions"][instance]:
                    metrics["functions"][instance][function]["avg_time"]=round(metrics["functions"][instance][function]["total_time"]/metrics["functions"][instance][function]["hits"],6)
                    metrics["functions"][instance][function]["hits_per_sec"]=(metrics["functions"][instance][function]["hits"]-self.metric_cache["functions"].get(function,metrics["functions"][instance][function]["hits"]))
                    self.metric_cache["functions"][function]=metrics["functions"][instance][function]["hits"]
            self.metric_cache["last_run"]=now
            self.metric_module.do(metrics)
            sleep(interval)

class Connector(Block):
    ''' A connector class which connects 2 queues to each other and takes care of shuffling the data between them.'''

    def __init__(self,name, source, destination):
        Block.__init__(self)
        self.proceed=Event()
        self.proceed.set()
        spawn (self.connector, source, destination)
        self.name=name
        self.hits = 0

    def connector(self, source, destination):
        '''Suffles data from source to destination.'''
        while self.block() == True:
            self.proceed.wait()
            destination.put(source.get())
            self.hits += 1

    def start(self):
        self.proceed.set()

    def pause(self):
        self.logging.info('Connector %s set to pause')
        self.proceed.clear()

    def unpause(self):
        self.logging.info('Connector %s set to unpause.')
        self.proceed.set()

    def stop(self):
        self.release()
