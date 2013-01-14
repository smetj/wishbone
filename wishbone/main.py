#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wishbone.py
#
#       Copyright 2012 Jelle Smet development@smetj.net
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
from multiprocessing import current_process
from string import lstrip
from toolkit import Block
from sys import exit
from time import time
from copy import deepcopy

class Metrics():

    def __init__(self):
        if self.metrics_dst == 'logging':
            self.doMetrics = self.logMetrics

    def doMetrics(self):
        self.logging.warn('You have not defined a valid metric emitter.')

    def logMetrics(self):
        while self.block():
            for module in self.modules:
                self.logging.info('Metrics %s: %s'%(module.name,str(module.metrics)))
            sleep(self.metrics_interval)

class Wishbone(Block, Metrics):
    '''
    **The main class in which the Wishbone modules are registered and managed.**
    
    

    Parameters:

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
        self.connectors=[]
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
            setattr(self, name, getattr (loaded_module, class_name)('Intance #%s:%s'%(self.__currentProcessName(),name), *args, **kwargs))
            self.modules.append(getattr (self, name))
            try:
                #Do a couple of checks to see whether the loaded module is compliant.
                self.modules[-1].metrics
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
        try:
            (src_class,src_queue)=source.split('.')
            (dst_class,dst_queue)=destination.split('.')
            src_instance=getattr(self,src_class)
            dst_instance=getattr(self,dst_class)
            self.connectors.append(spawn ( self.__connector, getattr(src_instance,src_queue), getattr(dst_instance,dst_queue), getattr(src_instance,"metrics")["queues"][src_queue], getattr(dst_instance,"metrics")["queues"][dst_queue] ))
        except Exception as err:
            self.logging.error("Problem connecting modules. Reason: %s"%(err))
            exit(1)
            
    def start(self):
        '''Function which starts all registered Wishbone modules.

        Function which runs over all registered instances/modules and tries to execute the start() function in order to let that module start
        to consume the messages of its inbox and execute the consume function on each message.
        This function blocks from exiting.
        '''

        for instance in self.__dict__:
            try:
                self.__dict__[instance].start()
            except:
                pass

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
                module.logMetrics()
            except:
                pass
            self.logging.debug('Waiting 1 second for module %s'%module.name)
            
            try:
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

    def __connector(self,source, destination, source_stats, destination_stats):
        '''Consumes data from source and puts it in destination.'''

        while self.block() == True:
            destination.put(source.get())
            source_stats["out"]+=1
            destination_stats["in"]+=1

    def __currentProcessName(self):
        '''return the current process name withought the Process- part'''
        if current_process().name == 'Process-1':
            return '0'
        else:
            return str(current_process().name)
