#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  zmqsubscriber.py
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
import zmq.green as zmq
from gevent import spawn


class ZMQTopicIn(Actor):

    '''**Subscribes to one or more ZeroMQ Topic publish modules.**

    Consumes data from one or more ZeroMQ publishers.

    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - host(string)("localhost")
           |  The host to submit to.

        - port(int)(19283)
           |  The port to submit to.

        - timeout(int)(1)
           |  The time in seconds to timeout when connecting

        - topic(string)("")
           |  The topic to subscribe to.


    Queues:

        - outbox
           |  Incoming events.

    '''

    def __init__(self, name, size=100, frequency=1, port=19283, timeout=10, topic=""):
        Actor.__init__(self, name, size, frequency)
        self.port = port
        self.timeout = timeout
        self.topic = topic
        self.pool.createQueue("outbox")

    def preHook(self):

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:%s" % self.port)
        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        spawn(self.drain)

    def drain(self):

        while self.loop():
            string = self.socket.recv()
            messagedata = string.split(" ")[1:]
            messagedata = " ".join(messagedata)
            event = self.createEvent()
            event.data = messagedata
            self.submit(event, self.pool.queue.outbox)
