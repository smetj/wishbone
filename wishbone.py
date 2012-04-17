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
import json
from jsonschema import Validator
from amqplib import client_0_8 as amqp
import gevent
from gevent import Greenlet, sleep, spawn
from gevent.queue import Queue
from gevent.server import DatagramServer
from gevent import monkey; monkey.patch_all()


class Wishbone():
    
    def __init__(self):
        self.lock=True
        self.__configureLogging()
        
    def registerBlock(self, module_name, class_name, name, *args, **kwargs):
        try:
            loaded_module = __import__(module_name)
            setattr(self, name, getattr (loaded_module, class_name)(name, self.block, *args, **kwargs))
        except Exception as err:
            print "Problem loading module: %s and class %s. Reason: %s" % ( module_name, class_name, err)

    def registerBroker(self, *args, **kwargs):
        self.broker = Broker(block=self.block, *args, **kwargs )
    
    def registerUDPServer(self, port='9000', *args, **kwargs):
        self.udp_server = UDPServer(port, *args, **kwargs)
    
    def connect(self,inbox,outbox):
        spawn ( self.__connector, inbox, outbox )
    
    def start(self):
        for instance in self.__dict__:
            try:
                self.__dict__[instance].start()
            except:
                pass
        while self.block() == True:
            sleep(0.01)

    def stop(self):
        self.lock=False
        for instance in self.__dict__:
            try:
                self.__dict__[instance].shutdown()
            except:
                pass
    
    def block(self):
        return self.lock
         
    def __connector(self,inbox, outbox):
        '''Consumes data from inbox and puts it in outbox.'''
        while self.block() == True:
                outbox.put(inbox.get())
        
    def __configureLogging(self,syslog=False,loglevel=logging.INFO):
        format=('%(asctime)s %(levelname)s %(name)s %(message)s')
        if syslog == False:
            logging.basicConfig(level=loglevel, format=format)
        else:
            logger = logging.getLogger()
            logger.setLevel(loglevel)
            syslog = SysLogHandler(address='/dev/log')
            formatter = logging.Formatter(format)
            syslog.setFormatter(formatter)
            logger.addHandler(syslog)


class Broker(Greenlet):
    '''Creates an object doing all broker I/O.  It's meant to be resillient to disconnects and broker unavailability.
    Data going to the broker goes into Broker.outgoing_queue.  Data coming from the broker is submitted to the scheduler_callback method'''
    
    def __init__(self, host, vhost, username, password, consume_queue='wishbone_in', produce_exchange='wishbone_out', routing_key='wishbone', block=None ):
        Greenlet.__init__(self)
        self.logging = logging.getLogger( 'Broker' )
        self.logging.info('Initiated')
        self.host=host
        self.vhost=vhost
        self.username=username
        self.password=password
        self.consume_queue = consume_queue
        self.produce_exchange = produce_exchange
        self.routing_key = routing_key
        self.block = block
        self.outbox=Queue(None)
        self.inbox=Queue(None)
        self.connected=False

    def __setup(self):
        self.conn = amqp.Connection(host="%s:5672"%(self.host), userid=self.username,password=self.password, virtual_host=self.vhost, insist=False)
        self.incoming = self.conn.channel()
        self.outgoing = self.conn.channel()
        self.logging.info('Connected to broker')
        
    def submitBroker(self):
        while self.block() == True:
            while self.connected == True:
                while self.outbox.qsize() > 0:
                    try:
                        self.logging.info('Submitting data to broker')
                        self.produce(self.outbox.get())
                    except:
                        break
                sleep(0.01)
            sleep(0.01)
                                
    def _run(self):
        self.logging.info('Started')
        night=0.5
        outgoing = gevent.spawn ( self.submitBroker )

        while self.block() == True:
            while self.connected==False:
                try:
                    if night < 512:
                        night *=2
                    self.__setup()
                    self.incoming.basic_consume(queue=self.consume_queue, callback=self.consume, consumer_tag='request')
                    self.connected=True
                    night=0.5
                except Exception as err:
                    self.connected=False
                    self.logging.warning('Connection to broker lost. Reason: %s. Try again in %s seconds.' % (err,night) )
                    sleep(night)
            while self.block() == True and self.connected == True:
                try:
                    self.incoming.wait()
                except Exception as err:
                    self.logging.warning('Connection to broker lost. Reason: %s' % err )
                    self.connected = False
                    self.incoming.close()
                    self.conn.close()
                    break
        
    def consume(self,doc):
        self.inbox.put(doc.body)
        self.logging.info('Data received from broker.')
        self.incoming.basic_ack(doc.delivery_tag)
        
    def produce(self,data):
        if self.connected == True:
            msg = amqp.Message(str(data[2]))
            msg.properties["delivery_mode"] = 2
            self.outgoing.basic_publish(msg,exchange=data[0],routing_key=data[1])
        else:
            raise Exception('Not Connected to broker')  

    def shutdown(self):
        self.logging.info('Shutdown')


class UDPServer(DatagramServer):
    def __init__(self, port, *args, **kwargs):
        DatagramServer.__init__(self, ':'+port, *args, **kwargs)
        self.logging = logging.getLogger( 'UDPServer' )
        self.logging.info ( 'started and listening on port %s' % port)
        self.inbox=Queue(None)        
        gevent.spawn(self.run)
    def handle(self, data, address):
        self.logging.info ('%s: Data received.' % (address[0]) )
        self.inbox.put(data)
    def run(self):
        self.serve_forever()


class PrimitiveActor(Greenlet):

    def __init__(self, name, block):
        Greenlet.__init__(self)
        self.logging = logging.getLogger( name )
        self.logging.info('Initiated.')
        self.block = block
        self.inbox = Queue(None)
        self.outbox = Queue(None)
        
    def _run(self):
        self.logging.info('Started.')
        while self.block() == True:
            message = self.inbox.get()
            self.consume(message)


class JSONValidator(PrimitiveActor):
    
    def __init__(self, name, block, *args, **kwargs):
        PrimitiveActor.__init__(self, name, block)
        self.schema = kwargs.get('schema',None)
        self.loadSchema()

    def loadSchema(self):
        file = open(self.schema,'r')
        data = file.readlines()
        file.close()
        self.schema=json.loads(''.join(data))

    def consume(self, message):
        try:
            data = json.loads(message)
            self.validateBroker(data)
            self.outbox.put(data)
        except Exception as err:
            self.logging.warning('Invalid data received and purged. Reason: %s' % (err))

    def validateBroker(self,data):
        checker = Validator()
        checker.validate(data,self.schema)

    def shutdown(self):
        self.logging.info('Shutdown')


class Compressor(PrimitiveActor):
    
    def __init__(self, name, block, *args, **kwargs):
        PrimitiveActor.__init__(self, name, block)
      
    def consume(self,doc):
        self.outbox.put((exchange, key, json.dumps(doc)))
       
    def shutdown(self):
        self.logging.info('Shutdown')


class Skeleton(PrimitiveActor):
    '''Skeleton class is a minimal Actor class which does nothing more than shoveling data from its inbox to its outbox.
    It can be used as an example/base for new blocks.'''
    
    def __init__(self, name, block, *args, **kwargs):
        PrimitiveActor.__init__(self, name, block)
    
    def consume(self,doc):
        self.outbox.put(doc)
       
    def shutdown(self):
        self.logging.info('Shutdown')
    
