#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  amqpout.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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

from gevent import monkey
monkey.patch_socket()
from wishbone import Actor
from amqp.connection import Connection as amqp_connection
from amqp import basic_message
from gevent import sleep
from wishbone.event import Bulk

class AMQPOut(Actor):

    '''**Produces messages to AMQP.**

    Submits messages to an AMQP message broker.

    If <exchange> is not provided, no exchange will be created during initialisation.
    If <queue> is not provided, queue will be created during initialisation

    If <exchange> and <queue> are provided, they will both be created and
    bound during initialisation.

    <exchange> and <queue> can be event lookup values.

    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - host(str)("localhost")
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

        - exchange_auto_delete(bool)(true)
           |  If set, the exchange is deleted when all queues have finished using it.

        - exchange_passive(bool)(false)
           |  If set, the server will not create the exchange. The client can use
           |  this to check whether an exchange exists without modifying the server state.

        - exchange_arguments(dict)({})
           |  Additional arguments for exchange declaration.

        - queue(str)("wishbone")
           |  The queue to declare and bind to <exchange>. This will also the
           |  the destination queue of the submitted messages unless
           |  <routing_key> is set to another value and <exchange_type> is
           |  "topic".

        - queue_durable(bool)(false)
           |  Declare a durable queue.

        - queue_exclusive(bool)(false)
           |  Declare an exclusive queue.

        - queue_auto_delete(bool)(true)
           |  Whether to autodelete the queue.

        - queue_declare(bool)(true)
           |  Whether to actually declare the queue.

        - queue_arguments(dict)({})
           |  Additional arguments for queue declaration.

        - routing_key(str)("")
           |  The routing key to use when submitting messages.

        - delivery_mode(int)(1)
           |  Sets the delivery mode of the messages.


    Queues:

        - inbox
           | Messages going to the defined broker.
    '''

    def __init__(self, actor_config, selection="@data",
                 host="localhost", port=5672, vhost="/", user="guest", password="guest",
                 exchange="", exchange_type="direct", exchange_durable=False, exchange_auto_delete=True, exchange_passive=False,
                 exchange_arguments={},
                 queue="wishbone", queue_durable=False, queue_exclusive=False, queue_auto_delete=True, queue_declare=True,
                 queue_arguments={},
                 routing_key="", delivery_mode=1):

        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        self._queue_arguments = dict(self.kwargs.queue_arguments)
        self._exchange_arguments = dict(self.kwargs.exchange_arguments)
        self.sendToBackground(self.setupConnectivity)

    def consume(self, event):

        if isinstance(event, Bulk):
            data = event.dumpFieldAsString(self.kwargs.selection)
        else:
            data = str(event.get(self.kwargs.selection))

        message = basic_message.Message(
                    body=data,
                    delivery_mode=self.kwargs.delivery_mode
                    )

        self.channel.basic_publish(message,
                                   exchange=self.kwargs.exchange,
                                   routing_key=self.kwargs.routing_key)
        sleep(0)

    def setupConnectivity(self):

        while self.loop():
            try:
                self.connection = amqp_connection(
                                    host=self.kwargs.host,
                                    port=self.kwargs.port,
                                    virtual_host=self.kwargs.vhost,
                                    userid=self.kwargs.user,
                                    password=self.kwargs.password
                                    )
                self.channel = self.connection.channel()

                if self.kwargs.exchange != "":
                    self.channel.exchange_declare(
                        self.kwargs.exchange,
                        self.kwargs.exchange_type,
                        durable=self.kwargs.exchange_durable,
                        auto_delete=self.kwargs.exchange_auto_delete,
                        passive=self.kwargs.exchange_passive,
                        arguments=self._exchange_arguments
                    )
                    self.logging.debug("Declared exchange %s." % (self.kwargs.exchange))

                if self.kwargs.queue_declare:
                    self.channel.queue_declare(
                        self.kwargs.queue,
                        durable=self.kwargs.queue_durable,
                        exclusive=self.kwargs.queue_exclusive,
                        auto_delete=self.kwargs.queue_auto_delete,
                        arguments=self._queue_arguments
                    )
                    self.logging.debug("Declared queue %s." % (self.kwargs.queue))

                if self.kwargs.exchange != "":
                    self.channel.queue_bind(
                        self.kwargs.queue,
                        self.kwargs.exchange,
                        routing_key=self.kwargs.routing_key
                    )
                    self.logging.debug("Bound queue %s to exchange %s." % (self.kwargs.queue, self.kwargs.exchange))

                self.logging.info("Connected to broker.")
            except Exception as err:
                self.logging.error("Failed to connect to broker.  Reason %s " % (err))
                sleep(1)
            else:
                break

    def postHook(self):
        try:
            self.connection.close()
        except:
            pass
