#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  zmqpushout.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
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
import zmq.green as zmq


class ZMQPushOut(Actor):

    '''**Pushes events out to one or more ZeroMQ pull modules.**

    Expects to connect with one or more wishbone.input.push modules.  This
    module can be started in client or server mode.  In server mode, it waits
    for incoming connections.  In client mode it connects to the defined
    clients.  Events are spread in a round robin pattern over all connections.

    Parameters:

        - mode(str)("server")
           |  The mode to run in.  Possible options are:
           |  - server: Binds to a port and listens.
           |  - client: Connects to a port.

        - interface(string)("0.0.0.0")
           |  The interface to bind to in server <mode>.

        - port(int)(19283)
           |  The port to bind to in server <mode>.

        - clients(list)([])
           |  A list of hostname:port entries to connect to.
           |  Only valid when running in "client" <mode>.


    Queues:

        - inbox
           |  Incoming events submitted to the outside.

    '''

    def __init__(self, actor_config, mode="server", interface="0.0.0.0", port=19283, clients=[]):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)

        if self.kwargs.mode == "server":
            self.socket.bind("tcp://*:%s" % self.kwargs.port)
            self.logging.info("Listening on port %s" % (self.kwargs.port))
        else:
            self.socket.connect("tcp://%s" % self.kwargs.clients[0])

    def consume(self, event):

        try:
            # self.socket.send(event.data, flags=zmq.NOBLOCK)
            self.socket.send(event.data)
        except Exception as err:
            self.logging.error("Failed to submit message.  Reason: %s" % (err))
