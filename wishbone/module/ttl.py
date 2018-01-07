#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ttl.py
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

from wishbone import Actor


class TTL(Actor):

    '''**Allows messages to pass a maximum number of times.**

    When a message has traveled through this module more than <ttl> times it
    will be submitted to the <ttl_exceeded> queue.

    Parameters::

        - ttl(int)(1)
           |  The maximum number of times an event is allowed
           |  to travel through.


    Queues::

        - inbox
           |  Incoming events.

        - outbox
           |  Outgoing events.

        - ttl_exceeded
           |  Events which passed the module more than <ttl> times.
    '''

    def __init__(self, actor_config, ttl=1):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("ttl_exceeded")

        self.__flush_lock = False

    def consume(self, event):

        if self.validateTTL(event):
            self.submit(event, self.pool.queue.outbox)
        else:
            self.logging.warning("Event TTL of %s exceeded in transit (%s) moving event to ttl_exceeded queue." % (event.getHeaderValue(self.name, "ttl_counter"), self.kwargs.ttl))
            self.submit(event, self.pool.queue.ttl_exceeded)

    def validateTTL(self, event):

        try:
            value = event.getHeaderValue(self.name, "ttl_counter")
            value += 1
            event.setHeaderValue("ttl_counter", value)
        except KeyError:
            event.setHeaderValue("ttl_counter", 1)
            value = 1

        if value > self.kwargs.ttl:
            return False
        else:
            return True
