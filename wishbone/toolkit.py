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
import pyes
from gevent import Greenlet
from gevent.queue import Queue
from gevent.event import Event
from copy import deepcopy
from pymongo import Connection
from gevent import monkey; monkey.patch_all()

class QueueFunctions():
    '''A base class for Wishbone Actor classes.  Shouldn't be called directly but is inherited by PrimitiveActor.'''
    
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
            except:
                setattr (self, queue, Queue)
                getattr (self, queue).put ( data )
        else:
            self.logging.warn('Invalid internal data structure detected. Data is purged. Turn on debugging to see datastructure.')
            self.logging.debug('Invalid data structure: %s' % (data))
    
    def sendRaw(self, data, queue='outbox'):
        '''Submits data to one of the mudule its queues.
        
        Allows you to bypass message integrity checking.  Its usage should be sparse, although it's usefull when you want to send data back 
        to a module as it would have come from the outside world.'''
        
        getattr (self, queue).put ( deepcopy(data) )
            
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
        Block.__init__(self)
        Greenlet.__init__(self)
        self.logging = logging.getLogger( name )
        self.logging.info('Initiated.')
        self.name=name
        self.inbox = Queue(None)
        self.outbox = Queue(None)
        self.stats={'msg': 0, 'min': 0, 'max': 0, 'avg': 0, 'total': 0}
        
    def _run(self):
        self.logging.info('Started.')
        while self.block() == True:
            try:
                data = self.inbox.get(timeout=0.1)
            except:
                pass
            else:
                t = stopwatch.Timer()
                self.consume(data)
                t.stop()
                self.stats['msg']+=1
                self.stats['total'] += t.elapsed
                self.stats['avg'] = self.stats['total'] / self.stats['msg']
                
                if self.stats['max'] == 0:
                    self.stats['max'] = t.elapsed
                elif t.elapsed > self.stats['max']:
                    self.stats['max'] = t.elapsed
                
                if self.stats['min'] == 0:
                    self.stats['min'] = t.elapsed
                if t.elapsed < self.stats['min']:
                    self.stats['min'] = t.elapsed
                    
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
        
        self.logging.info('Total messages: %s, Min: %s seconds, Max: %s seconds, Avg: %s seconds' % (self.stats['msg'], self.stats['min'], self.stats['max'], self.stats['avg']))
    
    def shutdown(self):
        '''A function which could be overridden by the Wisbone module.
        
        This function is called on shutdown.  Make sure you include self.lock=False otherwise that greenthread will hang on shutdown and never exit.'''
        self.logging.info('Shutdown')
        
class ESTools():
    '''A baseclass which offers ElasticSearch connectivity and functionality.'''
    
    def es_index(self, *args, **kwargs):
        '''Wrapper around ES.index()
        
        When ES is not available it tries to resubmit the document untill the general block is cancelled.'''
    
        while self.block() == True:
                while self.connected == False:
                    self.wait(0.5)                

                try:
                    id = self.conn.index(*args, **kwargs)
                    
                except Exception as err:
                    self.setupConnection()
                
                else:
                    break
        return id
    
    def setupConnection(self):
        '''Wrapper for calling __setupConnection.  Spawned into a greenlet so it doesn't block us.'''
        
        self.connected=False
        Greenlet.spawn(self.__setupConnection)
       
    def __setupConnection(self):
        '''Is called by setupConnection, tries to connect until succeeds or block is lifted.'''
        
        while self.block() == True:
            try:
                self.conn =  pyes.ES([self.host])
                if self.conn.collect_info() == False:
                    raise Exception ('Unable to connect.')
            except Exception as err:   
                self.logging.error('Could not connect to ElasticSearch. Waiting for a second.  Reason: %s' %(err))
                self.wait(timeout=1)
            else:
                self.logging.info('Connected')
                self.connected=True
                break

class MongoTools():
    '''A baseclass which offers MongoDB connectivity and functionality.'''
    
    def setupConnection(self):
        '''Wrapper for calling __setupConnection.  Spawned into a greenlet so it doesn't block us.'''
        self.connected=False
        Greenlet.spawn(self.__setupConnection)
    
    def __setupConnection(self):
        '''Is called by setupConnection, tries to connect until succeeds or block is lifted.'''
        
        while self.block() == True:
            try:
                self.conn = Connection( self.host, self.port, use_greenlets=True )
            except:
                self.logging.error('I could not connect to the MongoDB database.  Will try again in 1 second')
                self.wait(timeout=1)    
            else:
                self.logging.info('Connected')
                self.connected=True
                break
                
            
        
