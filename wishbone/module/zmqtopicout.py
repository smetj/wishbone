#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  zmqtopicout.py
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


class ZMQTopicOut(Actor):

    '''**Publishes data to one or more ZeroMQ Topic subscribe modules.**

    Expects wishbone.input.topic modules to take the initiative and connect to
    this module.  The clients subscribe to a topic of interest.  When multiple
    subscribers subscriber to the same topic, they will all receive the same
    messages resulting into a fanout messaging pattern.

    Parameters:

        - port(int)(19283)
           |  The port to bind to.

        - timeout(int)(1)
           |  The time in seconds to timeout when connecting.

        - topic(str)("")*
           |  The default topic to use when none is set in the header.


    Queues:

        - inbox
           |  Incoming events submitted to the outside.

    '''

    def __init__(self, actor_config, port=19283, timeout=10, topic=""):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:%s" % self.kwargs.port)

    def consume(self, event):

        try:
            self.socket.send("%s %s" % (self.kwargs.topic, event.data))
        except Exception as err:
            self.logging.error("Failed to submit message.  Reason %s" % (err))
            raise  # reraise the exception.
