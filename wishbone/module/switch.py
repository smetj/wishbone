#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  switch.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from wishbone.actor import Actor
from wishbone.module import FlowModule
from wishbone.error import ModuleInitFailure, ReservedName


class Switch(FlowModule):

    '''**Switch outgoing queues while forwarding events.**

    Forwards events to the desired outgoing queue based on the value of
    <outgoing>.

    The value of <outgoing> can be dynamically set in 2 ways:

        - Using a template function.

        - By sending an event to the <switch> queue with the value of
          <outgoing> stored under *data*.


    Parameters::

        - outgoing(str)("outbox")*
            |  The name of the queue to submit incoming events to.

    Queues::

        - inbox
           |  incoming events

        - switch
           |  incoming events to alter outgoing queue.

        - outbox*
           |  outgoing events

        - <connected_queue_1>
           |  outgoing events

        - <connected_queue_n>
           |  outgoing events
    '''

    def __init__(self, actor_config, outgoing="outbox"):

        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.pool.createQueue("switch")
        self.pool.createQueue("outbox")
        self.pool.queue.switch.disableFallThrough()
        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.switch, "switch")

        self.forbidden = ["inbox", "switch"]

    def preHook(self):

        if self.kwargs.outgoing in self.forbidden:
            raise ModuleInitFailure("Module parameter <outgoing> cannot have value '%s'." % (self.kwargs.outgoing))

        self.destination = self.kwargs.outgoing
        self._destination = self.kwargs.outgoing

    def consume(self, event):

        if self.kwargs.outgoing != self._destination:
            self._destination = self.kwargs.outgoing
            self.destination = self.kwargs.outgoing

        if self.destination in self.forbidden:
            raise ReservedName("Cannot forward incoming events to queue '%s'." % (self.destination))
        else:
            self.submit(event, self.destination)

    def switch(self, event):

        prefix = "<switch> queue received event"
        try:
            name = event.get("data")
            if self.pool.hasQueue(name):
                self.destination = name
                self.logging.info("%s. Outgoing messages forwarded to queue '%s'." % (prefix, name))
            else:
                self.logging.error("%s but module has no queue named '%s'." % (prefix, name))
        except KeyError:
            self.logging.error("%s but has no value key data." % (prefix))
