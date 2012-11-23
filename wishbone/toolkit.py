#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  toolkit.py
#  
#  Copyright 2012 Jelle Smet development@smetj.net
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

import logging
import stopwatch
from gevent import Greenlet
from gevent.queue import Queue
from gevent.event import Event
from gevent import sleep
from copy import deepcopy

class QueueFunctions():
    '''A base class for Wishbone Actor classes.  Shouldn't be called directly but is inherited by PrimitiveActor.'''
    
    def __init__(self):
        self.inbox = Queue(None)
        self.outbox = Queue(None)
        self.metrics={"functions":{},"queues":{"inbox":{"in":0,"out":0},"outbox":{"in":0,"out":0}}}
    
    def sendData(self, data, queue='outbox'):
        '''Submits data to one of the module its queues.
        
        The data send by this funtion is automatically checked on integrity, whether it has the right Wishbone data structure.  If that is not the case
        an exception is returned.
        
        Parameters:

            * queue:  Determines to which queue data should be send.  By default this is 'outbox'.
        '''
        
        if self.checkIntegrity(data):
            try:
                getattr (self, queue).put ( data )
                self.incrementMetric(queue, "in")
            except:
                setattr (self, queue, Queue)
                getattr (self, queue).put ( data )
        else:
            self.logging.warn('Invalid internal data structure detected. Data is purged. Turn on debugging to see datastructure.')
            self.logging.debug('Invalid data structure: %s' % (data))
    putData=sendData
    
    def sendRaw(self, data, queue='outbox'):
        '''Submits data to one of the module's queues.
        
        Allows you to bypass message integrity checking.  Its usage should be sparse, although it's usefull when you want to send data back 
        to a module as it would have come from the outside world.'''
        
        getattr (self, queue).put ( deepcopy(data) )
        self.incrementMetric(queue, "in")
    putRaw=sendRaw
    
    def getData(self, queue="inbox"):
        '''Gets data from the queue.'''
        data = getattr (self, queue).get()
        self.incrementMetric(queue, "out")
        return data
                
    def sendCommand(self, data, destination='*', queue='outbox'):
        '''Placeholder not implemented for the moment.'''
        
        self.outbox.put( (destination, data) )
        
    def checkIntegrity(self, data):
        '''Checks the integrity of the messages passed over the different queues.
        
        The format of the messages should be:
        
        { 'headers': {}, data: {} }'''
        
        if type(data) is dict:
            if len(data.keys()) == 2:
                if data.has_key('header') and data.has_key('data'):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def incrementMetric(self, queue, direction):
        '''Increments the counter of the queue with one in order to keep track of how many messages went through it.'''
        
        try:
            self.metrics["queues"][queue][direction]+=1
        except:
            if not hasattr(self, "metrics"):
                self.metrics={"functions":{},"queues":{"inbox":{"in":0,"out":0},"outbox":{"in":0,"out":0}}}
            self.metrics["queues"][queue]={"in":0,"out":0}
            self.metrics["queues"][queue][direction]+=1
    
    def createQueue(self, name):
        
        try:
            setattr(self,name,Queue(None))
            self.metrics["queues"][name]={"in":0,"out":0}
        except Exception as err:
            self.logging.warn('I could not create the queue named %s. Reason: %s'%(name, err))

    def logMetrics(self):
        self.logging.info("Queue metrics %s "%str(self.metrics))

class Block():
    '''A base class providing a global lock.'''
    
    def __init__(self):
        self.lock=Event()

    def block(self):
        '''A simple blocking function.'''
        
        if self.lock.isSet():
            return False
        else:
            return True

    def wait(self, timeout=None):
        '''Blocks from exiting until self.lock is set.'''
        
        self.lock.wait(timeout)

    def release(self):
        '''Set the lock flag which essentially unlocks.'''
        
        self.lock.set()

class PrimitiveActor(Greenlet, QueueFunctions, Block):
    '''A base class used to create Wishbone modules.
    
    This base class offers Wishbone specific functionalities and objects.

    Parameters:
        name:      Gives a name to the module
    '''

    def __init__(self, name):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.logging = logging.getLogger( name )
        self.logging.info('Initiated.')
        
    def timer(self, function, data):
        t = stopwatch.Timer()
        function(data)
        t.stop()
        try:
            self.metrics["functions"][function.__name__]
        except:
            self.metrics["functions"][function.__name__]={"called":0,"total_time":0,"max_time":0,"min_time":0,"cur_time":0,"avg_time":0}
            
        self.metrics["functions"][function.__name__]['total_time'] += t.elapsed
        self.metrics["functions"][function.__name__]['called'] += 1
        self.metrics["functions"][function.__name__]['avg_time'] += self.metrics["functions"][function.__name__]['total_time'] / self.metrics["functions"][function.__name__]['called']

        if self.metrics["functions"][function.__name__]['max_time'] == 0:
            self.metrics["functions"][function.__name__]['max_time'] = t.elapsed
        elif t.elapsed > self.metrics["functions"][function.__name__]['max_time']:
            self.metrics["functions"][function.__name__]['max_time'] = t.elapsed
        
        if self.metrics["functions"][function.__name__]['min_time'] == 0:
            self.metrics["functions"][function.__name__]['min_time'] = t.elapsed
        if t.elapsed < self.metrics["functions"][function.__name__]['min_time']:
            self.metrics["functions"][function.__name__]['min_time'] = t.elapsed
         
    def _run(self):
        self.logging.info('Started.')
        while self.block() == True:
            data = self.getData("inbox")
            self.timer(self.consume, data)                            
                    
    def consume(self, *args, **kwargs):
        '''A function which should be overridden by the Wishbone module.
        
        This function, when called throws an exception.
        '''
        raise Exception ('You have no consume function in your class.')
        
    def command(self, *args, **kwargs):
        '''A placeholder not implemented for the moment.'''
        
        self.logging.info('Initiated.')
        self.name=name
        self.block = block
        self.inbox = Queue(None)
        self.outbox = Queue(None)

    def logMetrics(self):
        '''Generates a line with metrics of the spefic module.'''
        
        self.logging.info(str(self.metrics))
    
    def shutdown(self):
        '''A function which could be overridden by the Wisbone module.
        
        This function is called on shutdown.  Make sure you include self.lock=False otherwise that greenthread will hang on shutdown and never exit.'''
        self.logging.info('Shutdown')
