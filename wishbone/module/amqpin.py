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

from wishbone import Actor
from wishbone.error import QueueFull, QueueEmpty
from haigha.connection import Connection as amqp_connection
from gevent import sleep, spawn


class AMQPIn(Actor):

    '''**Consumes messages from AMQP.**

    Consumes messages from an AMQP message broker.
    The declared <exchange> and <queue> will be bound to each other.

    Parameters:

        -   name(str)
            The instance name when initiated.

        -   size(int)
            The size of all module queues.

        -   host(str) "localhost"
            The host broker to connect to.

        -   port(int)(5672)
            The port to connect to.

        -   vhost(str)("/")
            The virtual host to connect to.

        -   user(str)("guest")
            The username to authenticate.

        -   password(str)("guest")
            The password to authenticate.

        -   exchange(str)("")
            The exchange to declare.

        -   exchange_type(str)("direct")
            The exchange type to create. (direct, topic, fanout)

        -   exchange_durable(bool)(false)
            Declare a durable exchange.

        -   queue(str)("wishbone")
            The queue to declare and ultimately consume.

        -   queue_durable(bool)(false)
            Declare a durable queue.

        -   queue_exclusive(bool)(false)
            Declare an exclusive queue.

        -   queue_auto_delete(bool)(true)
            Whether to autodelete the queue.

        -   routing_key(str)("")
            The routing key to use in case of a "topic" exchange.
            When the exchange is type "direct" the routing key is always equal
            to the <queue> value.

        -

    Queues:

        - outbox:    Messages coming from the defined broker.
    '''

    def __init__(self, name, size, host="localhost", port=5672, vhost="/", user="guest", password="guest",
                 exchange="", exchange_type="direct", exchange_durable=False,
                 queue="wishbone", queue_durable=False, queue_exclusive=False, queue_auto_delete=True,
                 routing_key=""):
        Actor.__init__(self, name, size)
        self.name = name
        self.size = size
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
        self.routing_key = routing_key

        self.pool.createQueue("outbox")
        self.pool.createQueue("ack")

    def preHook(self):

        spawn(self.setupConnectivity)
        spawn(self.messagePump)

    def consume(self, message):
        print message

    def setupConnectivity(self):

        while self.loop():
            try:
                self.connection = amqp_connection(host=self.host, port=self.port, vhost=self.vhost, user=self.user, password=self.password, transport="gevent", debug=True)
                self.channel = self.connection.channel()
                if self.exchange != "":
                    self.channel.exchange.declare(self.exchange, self.exchange_type, durable=self.exchange_durable)
                self.channel.queue.declare(self.queue, durable=self.queue_durable, exclusive=self.queue_exclusive, auto_delete=self.queue_auto_delete)
                if self.exchange != "":
                    self.channel.queue.bind(self.queue, self.exchange, routing_key=self.routing_key)
                self.channel.basic.consume(self.queue, self.consume)
                self.logging.info("Connected to broker on %s " % (self.host))
                break
            except Exception as err:
                self.logging.error("Failed to connect to broker.  Reason %s " % (err))
                sleep(1)

    def messagePump(self):
        while self.loop():
            try:
                self.connection.read_frames()
            except:
                sleep(0.1)

    def postHook(self):
        self.connection.close()