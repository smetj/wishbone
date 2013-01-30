#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  broker.py
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
from wishbone.toolkit import QueueFunctions, Block, TimeFunctions
from gevent import Greenlet, spawn, sleep
from gevent.queue import Queue
from amqplib import client_0_8 as amqp
from amqplib.client_0_8.exceptions import AMQPChannelException, AMQPConnectionException
from gevent import monkey;monkey.patch_all()

class Broker(Greenlet, QueueFunctions, Block, TimeFunctions):
    '''**A Wishbone IO module which handles AMQP0.8 input and output.**
    
    This module handles the IO from and to a message broker.  This module has
    specifically been tested against RabbitMQ.  The module is meant to be resilient
    against disconnects and broker unavailability.
    
    The module will currently not create any missing queues or exchanges.
    
    Acknowledging can can done in 2 ways:
    
    - Messages which arrive to outbox and which have an acknowledge tag in the header 
      will be acknowledged with the broker.
    
    - When a broker_tag is submitted to the "acknowledge" queue using sendRaw(),
      then the message will be acknowledged at the broker.
    
    All incoming messages should have at least following header:
        
        {'header':{'broker_exchange':name, 'broker_key':name, 'broker_tag':tag}}    
        
        - broker_exchange:    The exchange to which data should be submitted.
        - broker_key:         The routing key used when submitting data.
        - broker_tag:         The tag used to acknowledge the message from the broker.
        
    Parameters:        

        - name (str):           The instance name when initiated.
        - host (str):           The name or IP of the broker.
        - vhost (str):          The virtual host of the broker. By default this is '/'.
        - username (str):       The username to connect to the broker.  By default this is 'guest'.
        - password (str):       The password to connect to the broker.  By default this is 'guest'.
        - consume_queue (str):  The queue which should be consumed. By default this is "wishbone_in".
        - prefetch_count (str): The amount of messages consumed from the queue at once.
        - no_ack (str):         No acknowledgements required? By default this is False (means acknowledgements are required.)
        - delivery_mode (int):  The message delivery mode.  1 is Non-persistent, 2 is Persistent. Default=2
        - auto_create (bool):   When True missing exchanges and queues will be created.

    Queues:
        
        - inbox:              Messages coming from the broker.
        - outbox:             Messages destined for the broker.
        - acknowledge:        Message tags to acknowledge with the broker.
    '''
    
    def __init__(self, name, host, vhost='/', username='guest', password='guest', prefetch_count=1, no_ack=False, consume_queue='wishbone_in', delivery_mode=2, auto_create=True ):
    
        Greenlet.__init__(self)
        Block.__init__(self)
        QueueFunctions.__init__(self)
        self.name=name
        self.logging = logging.getLogger( self.name )
        self.logging.info('Initiated')
        self.host=host
        self.vhost=vhost
        self.username=username
        self.password=password
        self.prefetch_count=prefetch_count
        self.no_ack=no_ack
        self.consume_queue = consume_queue
        self.delivery_mode=delivery_mode
        self.auto_create=auto_create
        #self.createQueue("acknowledge") #why?
        self.acknowledge=Queue()

    def _run(self):
        '''
        Blocking function which start consumption and producing of data.  It is executed when issuing the Greenlet start()
        '''
        
        self.logging.info('Started')
        self.setup()
        outgoing = spawn(self.submitBroker)
        ack = spawn(self.acknowledgeMessage)        
        
        while self.block() == True:
            try:
                self.incoming.wait()
            except:
                self.setup()

    def safe(fn):
        def do(self, message):
            while self.block() == True:
                try:
                    fn(self, message)
                    break
                except AMQPChannelException as err:
                    #(404, u"NOT_FOUND - no queue 'xwishbone' in vhost '/'", (60, 20), 'Channel.basic_consume')
                    self.logging.error("AMQP error. Reason: %s"%(err))
                    self.createQueue()
                    self.createExchange()
                    self.createBinding()
                except AMQPConnectionException as err: 
                    self.logging.error("AMQP error. Reason: %s"%(err))
                except Exception as err:
                    self.logging.error("AMQP error. Reason: %s"%(err))
                self.setup()
        return do        

    @safe
    def createQueue(self, *args, **kwargs):
        pass
    
    @safe
    def createExchange(self, *args, **kwargs):
        pass
    
    @safe
    def createBinding(self, *args, **kwargs):
        pass
    
    def setup(self):
        '''Handles connection and channel creation.
        '''
        while self.block() == True:
            try:
                self.conn = amqp.Connection(host="%s:5672"%(self.host), userid=self.username,password=self.password, virtual_host=self.vhost, insist=False)
                self.incoming = self.conn.channel()
                self.incoming.basic_qos(prefetch_size=0, prefetch_count=self.prefetch_count, a_global=False)                
                self.incoming.basic_consume(queue=self.consume_queue, callback=self.consume, no_ack=self.no_ack)
                self.outgoing = self.conn.channel()
                self.logging.info('Connected to broker')
                break
                
            except Exception as err:
                self.logging.error("AMQP error. Reason: %s"%(err))
                sleep(1)
                
    def submitBroker(self):
        '''Submits all data from self.outbox into the broker by calling the produce() funtion.
        '''
        while self.block() == True:
            self.produce(self.getData("outbox"))
    
    def acknowledgeMessage(self):
        '''Acknowledges messages
        '''       

        while self.block() == True:
            self.ack(self.getData("acknowledge"))
    
    @safe
    def ack(self, ack):
        self.incoming.basic_ack(ack)
            
    @TimeFunctions.do
    def consume(self,doc):
        '''Is called upon each message coming from the broker infrastructure.
        
        It also makes sure the incoming data is encapsulated in the right Wishbone format.
        When successful, this function acknowledges the message from the broker.
        '''
        self.putData({'header':{'broker_tag':doc.delivery_tag},'data':doc.body}, queue='inbox')
        self.logging.debug('Data received from broker.')
        sleep()
    
    @safe
    def produce(self,message):
        '''Is called upon each message going to to the broker infrastructure.
        
        This function is called by the consume() function.  If the correct header info isn't present (but that would be odd at this point), the data is purged.
        '''
        if message["header"].has_key('broker_exchange') and message["header"].has_key('broker_key'):            
            msg = amqp.Message(str(message['data']))
            msg.properties["delivery_mode"] = self.delivery_mode
            self.outgoing.basic_publish(msg,exchange=message['header']['broker_exchange'],routing_key=message['header']['broker_key'])
            if message['header'].has_key('broker_tag') and self.no_ack == False:
                self.incoming.basic_ack(message['header']['broker_tag'])
        else:
            self.logging.warn('Received data for broker without exchange or routing key in header. Purged.')
            if message['header'].has_key('broker_tag') and self.no_ack == False:
                self.incoming.basic_ack(message['header']['broker_tag'])

    def shutdown(self):
        '''This function is called on shutdown().'''
        
        try:
             self.incoming.basic_cancel('request')
        except:
            pass
        self.logging.info('Shutdown')
