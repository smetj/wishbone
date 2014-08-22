#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  amqpout.py
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

from gevent import monkey; monkey.patch_socket()
from wishbone import Actor
from amqp.connection import Connection as amqp_connection
from amqp import basic_message
from gevent import sleep, spawn


class AMQPOut(Actor):

    '''**Produces messages to AMQP.**

    Submits messages to an AMQP message broker. The declared <exchange> and
    <queue> will be bound to each other.

    If no exchange name is provided, no exchange will be created. If
    event["header"][<name>]["exchange"] exists it will override whatever is
    defined in <exchange>.

    If no queue name is provided, no queue will be create. if
    event["header"][<name>]["queue"] exists it will override whatever is
    defined in <queue>.


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - host(str) "localhost"
           |  The host broker to connect to.

        - port(int)(5672)
           |  The port to connect to.

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

        - queue(str)("")
           |  The queue to declare and ultimately sumit messages to.

        - queue_durable(bool)(false)
           |  Declare a durable queue.

        - queue_exclusive(bool)(false)
           |  Declare an exclusive queue.

        - queue_auto_delete(bool)(true)
           |  Whether to autodelete the queue.


    Queues:

        - inbox
           | Messages going to the defined broker.
    '''

    def __init__(self, name, size=100, frequency=1, host="localhost", port=5672, vhost="/", user="guest", password="guest",
                 exchange="", exchange_type="direct", exchange_durable=False,
                 queue="", queue_durable=False, queue_exclusive=False, queue_auto_delete=True,
                 routing_key=""):
        Actor.__init__(self, name, size, frequency)
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

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        spawn(self.setupConnectivity)

    def consume(self, event):

        # self.channel.basic_publish(str(event["data"]),
        #     exchange=event["header"][self.name].get("exchange", self.exchange),
        #     routing_key=event["header"][self.name].get("routing_key", self.routing_key))

        message = basic_message.Message(body=str(event["data"]))
        self.channel.basic_publish(message,
                                   exchange=self.exchange,
                                   routing_key=self.routing_key)

    def setupConnectivity(self):

        while self.loop():
            try:
                self.connection = amqp_connection(host=self.host, port=self.port, virtual_host=self.vhost, userid=self.user, password=self.password)
                self.channel = self.connection.channel()

                if self.exchange != "":
                    self.channel.exchange_declare(self.exchange, self.exchange_type, durable=self.exchange_durable)
                    self.logging.debug("Declared exchange %s." % (self.exchange))
                if self.queue != "":
                    self.channel.queue_declare(self.queue, durable=self.queue_durable, exclusive=self.queue_exclusive, auto_delete=self.queue_auto_delete)
                    self.logging.debug("Declared queue %s." % (self.queue))
                if self.exchange != "" and self.queue != "":
                    self.channel.queue.bind(self.queue, self.exchange, routing_key=self.routing_key)
                    self.logging.debug("Bound queue %s to exchange %s." % (self.queue, self.exchange))

                self.logging.info("Connected to broker.")
                break
            except Exception as err:
                self.logging.error("Failed to connect to broker.  Reason %s " % (err))
                sleep(1)

    def postHook(self):
        try:
            self.connection.close()
        except:
            pass