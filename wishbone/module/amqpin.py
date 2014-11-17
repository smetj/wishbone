#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  amqpin.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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

from gevent import monkey;monkey.patch_socket()
from wishbone import Actor
from wishbone.error import QueueEmpty
from amqp.connection import Connection as amqp_connection
from gevent import sleep, spawn


class AMQPIn(Actor):

    '''**Consumes messages from AMQP.**

    Consumes messages from an AMQP message broker.
    The declared <exchange> and <queue> will be bound to each other.

    Parameters:

        - host(str)("localhost")
           | The host to connect to.

        - port(int)(5672)
           | The port to connect to.

        - vhost(str)("/")
           |  The virtual host to connect to.

        - user(str)("guest")
           |  The username to authenticate.

        - password(str)("guest")
           |  The password to authenticate.

        - exchange(str)("")
           |  The exchange to declare.

        - exchange_type(str)("direct")
           |  The exchange type to create. (direct, topic, fanout)

        - exchange_durable(bool)(false)
           |  Declare a durable exchange.

        - queue(str)("wishbone")
           |  The queue to declare and ultimately consume.

        - queue_durable(bool)(false)
           |  Declare a durable queue.

        - queue_exclusive(bool)(false)
           |  Declare an exclusive queue.

        - queue_auto_delete(bool)(true)
           |  Whether to autodelete the queue.

        - queue_declare(bool)(true)
           |  Whether to actually declare the queue.

        - routing_key(str)("")
           |  The routing key to use in case of a "topic" exchange.
           | When the exchange is type "direct" the routing key is always equal
           | to the <queue> value.

        - prefetch_count(int)(1)
           |  Prefetch count value to consume messages from queue.

        - no_ack(bool)(false)
           |  Override acknowledgement requirement.


    Queues:

        - outbox
           |  Messages coming from the defined broker.

        - ack
           |  Messages to acknowledge (requires the delivery_tag)
    '''

    def __init__(self, actor_config host="localhost", port=5672, vhost="/", user="guest", password="guest",
                 exchange="", exchange_type="direct", exchange_durable=False,
                 queue="wishbone", queue_durable=False, queue_exclusive=False, queue_auto_delete=True, queue_declare=True,
                 routing_key="", prefetch_count=1, no_ack=False):
        Actor.__init__(self, actor_config)
        self.host = host
        self.port = port
        self.vhost = vhost
        self.user = user
        self.password = password
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.exchange_durable = exchange_durable
        self.queue = queue
        self.queue_durable = queue_durable
        self.queue_exclusive = queue_exclusive
        self.queue_auto_delete = queue_auto_delete
        self.queue_declare = queue_declare
        self.routing_key = routing_key
        self.prefetch_count = prefetch_count
        self.no_ack = no_ack

        self.pool.createQueue("outbox")
        self.pool.createQueue("ack")
        self.pool.queue.ack.disableFallThrough()

    def preHook(self):
        spawn(self.setupConnectivity)
        spawn(self.handleAcknowledgements)

    def consume(self, message):
        event = self.createEvent()
        event.setHeaderValue(self.name, delivery_tag, message.delivery_info["delivery_tag"])
        event.data = str(message.body)
        self.submit(event, self.pool.queue.outbox)

    def setupConnectivity(self):

        while self.loop():
            try:
                self.connection = amqp_connection(host=self.host, port=self.port, virtual_host=self.vhost, userid=self.user, password=self.password)
                self.channel = self.connection.channel()
                if self.exchange != "":
                    self.channel.exchange_declare(self.exchange, self.exchange_type, durable=self.exchange_durable)
                    self.logging.debug("Declared exchange %s." % (self.exchange))

                if self.queue_declare:
                    self.channel.queue_declare(self.queue, durable=self.queue_durable, exclusive=self.queue_exclusive, auto_delete=self.queue_auto_delete)
                    self.logging.debug("Declared queue %s." % (self.queue))
                if self.exchange != "":
                    self.channel.queue.bind(self.queue, self.exchange, routing_key=self.routing_key)
                    self.logging.debug("Bound queue %s to exchange %s." % (self.queue, self.exchange))
                self.channel.basic_qos(prefetch_size=0, prefetch_count=self.prefetch_count, a_global=False)
                self.channel.basic_consume(self.queue, callback=self.consume, no_ack=self.no_ack)
                self.logging.info("Connected to broker.")
            except Exception as err:
                self.logging.error("Failed to connect to broker.  Reason %s " % (err))
                sleep(1)
            else:
                spawn(self.drain)
                break

    def drain(self):
        while self.loop():
            try:
                self.connection.drain_events()
            except Exception as err:
                self.logging.error("Problem connecting to broker.  Reason: %s" % (err))
                sleep(1)
                spawn(self.setupConnectivity)
                break

    def handleAcknowledgements(self):
        while self.loop():
            try:
                event = self.pool.queue.ack.get()
            except QueueEmpty as err:
                err.waitUntilContent()
            else:
                try:
                    self.channel.basic_ack(event.getHeaderValue(self.name, "delivery_tag"))
                except Exception as err:
                    self.pool.queue.ack.rescue(event)
                    self.logging.error("Failed to acknowledge message.  Reason: %s." % (err))
                    sleep(0.5)

    def postHook(self):
        try:
            self.connection.close()
        except:
            pass
