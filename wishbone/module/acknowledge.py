#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  acknowledge.py
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
from gevent.lock import Semaphore
from wishbone.lookup import EventLookup
from random import SystemRandom
import string

class AckList(object):

    def __init__(self):

        self.ack_table = []
        self.lock = Semaphore()

    def ack(self, value):

        with self.lock:
            if value in self.ack_table:
                self.ack_table.remove(value)
                return True
            else:
                return False

    def unack(self, value):

        with self.lock:
            if value in self.ack_table:
                return False
            else:
                self.ack_table.append(value)
                return True



class Acknowledge(Actor):

    '''**Lets events pass or not based on some event value present or not in a lookup table.**

    This module stores a value <ack_id> from passing events in a list and
    only let's events go through for which the <ack_id> value is not in the
    list.

    <ack_id> can be removed from the list by sending the event into the
    <acknowledge> queue.

    <ack_id> should some unique identifier to make sure that any following
    <modules are not processing events with the same datastructure.

    Typically, downstream modules's <successful> and/or <failed> queues are
    sending events to the <acknowledge> queue.

    Parameters:

        - ack_id(EventLookup("@data"))
           |  A value stored somewhere in the event which then acts as the
           |  ack_id. It possibly makes only sense to define an EventLookup
           |  value here.

    Queues:

        - inbox
           |  Incoming events

        - outbox
           |  Outgoing events

        - acknowledge
            | Acknowledge events

        - dropped
            | Where events go to when unacknowledged

    '''

    def __init__(self, actor_config, ack_id=None):

        if ack_id is None:
            event_lookup_string = ''.join(SystemRandom().choice(string.ascii_lowercase) for _ in range(4))
            actor_config.lookup[event_lookup_string] = EventLookup()
            ack_id = "%s('@data')" % (event_lookup_string)

        Actor.__init__(self, actor_config)
        self.ack_id_ref = ack_id

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("acknowledge")
        self.pool.createQueue("dropped")
        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.acknowledge, "acknowledge")
        self.ack_table = AckList()

    def consume(self, event):

        if self.kwargs.ack_id is None:
            self.logging.warning("Incoming event with <ack_id> %s does not seem to exist.  Returns a None value. Event passing through." % (self.ack_id_ref))
            self.pool.queue.outbox.put(event)
        elif self.ack_table.unack(self.kwargs.ack_id):
            self.logging.debug("Event unacknowledged with <ack_id> '%s'." % (self.kwargs.ack_id))
            self.pool.queue.outbox.put(event)
        else:
            self.logging.debug("Event with still unacknowledged <ack_id> '%s' send to <dropped> queue." % (self.kwargs.ack_id))
            self.pool.queue.dropped.put(event)


    def acknowledge(self, event):
        if self.kwargs.ack_id is None:
            self.logging.warning("Incoming acknowledge event with <ack_id> %s does not seem to exist.  Returns a None value. Nothing to do." % (self.ack_id_ref))
        elif self.ack_table.ack(self.kwargs.ack_id):
            self.logging.debug("Event acknowledged with <ack_id> '%s'." % (self.kwargs.ack_id))
        else:
            self.logging.debug("Event with <ack_id> '%s' received but was not previously acknowledged." % (self.kwargs.ack_id))

    def postHook(self):

        self.logging.debug("The ack table has %s events unacknowledged." % (len(self.ack_table.ack_table)))
