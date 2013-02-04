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
from gevent import spawn, sleep
from gevent.queue import Queue
from gevent.event import Event
from multiprocessing import current_process
from string import lstrip
from toolkit import Block
from sys import exit
from time import time
from copy import deepcopy
from time import time
from prettytable import PrettyTable

class Metrics():

    def __init__(self):
        self.cache={"last_run":time(),"functions":{}}
        if self.metrics_dst == 'logging':
            self.doMetrics = self.logMetrics
        if self.metrics_dst == 'table':
            self.doMetrics = self.tableMetrics

    def doMetrics(self):
        self.logging.warn('You have not defined a valid metric emitter.')

    def logMetrics(self):
        while self.block():
            self.logging.info(self.collectMetrics())
            sleep(self.metrics_interval)
    
    def tableMetrics(self):
        #{'functions': 
        #    {   u'Intance #0:stdout': {'consume': {'total_time': 0.00074744224548339844, 'hits_per_sec': 0.0, 'hits': 9, 'avg_time': 8.3049138387044266e-05}}, 
        #        u'Intance #0:broker': {'consumeMessage': {'total_time': 0.0026221275329589844, 'hits_per_sec': 0.0, 'hits': 9, 'avg_time': 0.00029134750366210938}}},
        #'connectors':
        #    {   u'broker.inbox->stdout.inbox': 9}}

        #{'functions': {u'Intance #0:stdout': {}, u'Intance #0:broker': {}}, 'connectors': {u'broker.inbox->stdout.inbox': 0}}
        
        while self.block():
        
            dataset = self.collectMetrics()

            func_table = PrettyTable(["Instance", "Function", "Total time", "Hits per second","Hits","Average time"])
            for instance in dataset["functions"]:
                for function in dataset["functions"][instance]:
                    func_table.add_row([instance, function, dataset["functions"][instance][function]["total_time"], dataset["functions"][instance][function]["hits_per_sec"], dataset["functions"][instance][function]["hits"], dataset["functions"][instance][function]["avg_time"]])
            
            conn_table = PrettyTable(["Connector","Hits"])
            for connector in dataset["connectors"]:
                conn_table.add_row([connector,dataset["connectors"][connector]])
            print "Function metrics:"
            print 
            print func_table
            print
            print "Connector metrics:"
            print conn_table
            sleep(self.metrics_interval)
    
    def collectMetrics(self):
        now = time()
        metrics={"functions":{},"connectors":{}}

        for module in self.modules:
            metrics["functions"][module.name]=module.metrics
            
        for connector in self.connectors:
            metrics["connectors"][connector] = self.connectors[connector].hits

        for instance in metrics["functions"]:
            for function in metrics["functions"][instance]:
                metrics["functions"][instance][function]["avg_time"]=metrics["functions"][instance][function]["total_time"]/metrics["functions"][instance][function]["hits"]
                metrics["functions"][instance][function]["hits_per_sec"]=(metrics["functions"][instance][function]["hits"]-self.cache["functions"].get(function,0))/(now-self.cache["last_run"])
                self.cache["functions"][function]=metrics["functions"][instance][function]["hits"]
        self.cache["last_run"]=now
        return metrics

class Wishbone(Block, Metrics):
    '''
    **The main class in which the Wishbone modules are registered and managed.**



    Parameters:

        * syslog (bool):                Enable/disable logging to syslog.
        * metrics (bool):               Enable/disable metrics.
        * metrics_interval (int):       The interval metrics need to be emitted.
        * metrics_dst (str):            The destination to write metrics to: [logging]
    '''

    def __init__(self, syslog=False, metrics=True, metrics_interval=10, metrics_dst="logging"):
        
        self.metrics=metrics
        self.metrics_interval=metrics_interval
        self.metrics_dst=metrics_dst

        self.logging = logging.getLogger( 'Wishbone' )
        Block.__init__(self)
        Metrics.__init__(self)

        signal.signal(signal.SIGTERM, self.stop)

        self.modules=[]
        self.connectors={}
        self.run=self.start

    def registerModule(self, config, *args, **kwargs):
        '''Registers a Wishbone Module into the framework.  All modules used within Wishbone should be registered through this function.

        This function receives a tuple containing 3 values.  Any further args or kwargs are used to initialize the actual module you register.

        The config parameter should be a tuple of 3 strings:

            (module, class, name)

            * module:     The name of the module to import.
            * class:      The name of the class to initialize
            * name:       The name under which the module should be initialized.

            *args and **kwargs are passed to the class which is initialized.

        self.modules contains a list of all registered modules.  Also, each registered module is registered under self.name, where name is last
        value of the tuple.'''

        module_name = config[0]
        class_name = config[1]
        name = config[2]
        try:
            loaded_module = import_module(module_name)
            setattr(self, name, getattr (loaded_module, class_name)('Intance #%s:%s'%(self.getCurrentProcessName(),name), *args, **kwargs))
            self.modules.append(getattr (self, name))
            try:
                #Do a couple of checks to see whether the loaded module is compliant.
                self.modules[-1].inbox
                self.modules[-1].outbox
            except:
                raise Exception("You might have to load QueueFunctions base class into this class.")
        except Exception as err:
            self.logging.error("Problem loading module: %s and class %s. Reason: %s" % ( module_name, class_name, err))
            exit(1)

    def connect(self, source, destination):
        '''Creates a new background Greenthread which continuously consumes all messages from source into destination.

        Both source and destination should be strings.
        '''

        (src_class,src_queue)=source.split('.')
        (dst_class,dst_queue)=destination.split('.')
        src_instance = getattr(self,src_class)
        dst_instance = getattr(self,dst_class)
        src_queue = getattr(src_instance,src_queue)
        dst_queue = getattr(dst_instance,dst_queue)
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
                module.start()
            except:
                pass

        for connector in self.connectors.keys():
            self.connectors[connector].start()

        if self.metrics == True:
            self.logging.debug('Metrics enabled')
            spawn(self.doMetrics)
        else:
            self.logging.debug('Metrics disabled.')

        while self.block():
            self.wait(0.1)

    def stop(self,a,b):
        '''Function which stops all registered Wishbone modules.

        Function which runs over all registered instances/modules and tries to execute its stop() function in order to stop that module.
        '''

        self.logging.info('Stop received.')
        for module in self.modules:
            module.release()
            module.shutdown()

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
        self.logging.info(self.collectMetrics())
        self.release()

    def getCurrentProcessName(self):
        '''return the current process name withought the Process- part'''
        if current_process().name == 'Process-1':
            return '0'
        else:
            return str(current_process().name)

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
