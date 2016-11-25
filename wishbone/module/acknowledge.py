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


class Acknowledge(Actor):

    '''**Lets events pass or not based on some event value present or not in a lookup table.**

    This module stores a value <ack_value> from passing events in a list and
    only let's events go through for which the <ack_value> value is not in the
    list.

    <ack_value> can be removed from the list by sending the event into the
    <acknowledge> queue.

    <ack_value> should some unique identifier to make sure that any following
    <modules are not processing events with the same datastructure.

    Typically, downstream modules's <successful> and/or <failed> queues are
    sending events to the <acknowledge> queue.

    Parameters:

        - ack_value(str)(None)*
           |  The key


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

    def __init__(self, actor_config, ack_value=None):
        Actor.__init__(self, actor_config)
        self.ack_value_ref = ack_value

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("acknowledge")
        self.pool.createQueue("dropped")
        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.acknowledge, "acknowledge")
        self.ack_table = []

    def consume(self, event):

        if self.kwargs.ack_value is None:
            self.logging.warning("Incoming event with <ack_value> %s does not seem to exist.  Returns a None value. Event passing through." % (self.ack_value_ref))
            self.pool.queue.outbox.put(event)
        elif self.kwargs.ack_value in self.ack_table:
            self.logging.debug("Event with unacknowledged <ack_value> '%s'. Sent to 'dropped' queue." % (self.kwargs.ack_value))
            self.pool.queue.dropped.put(event)
        else:
            self.ack_table.append(self.kwargs.ack_value)
            self.logging.debug("Added <ack_value> '%s' to table." % (self.kwargs.ack_value))
            self.pool.queue.outbox.put(event)

    def acknowledge(self, event):
        if self.kwargs.ack_value is None:
            self.logging.warning("Incoming acknowledge event with <ack_value> %s does not seem to exist.  Returns a None value. Nothing to do." % (self.ack_value_ref))
        elif self.kwargs.ack_value in self.ack_table:
            self.logging.debug("Event acknowledged with <ack_value> '%s'." % (self.kwargs.ack_value))
            self.ack_table.remove(self.kwargs.ack_value)
        else:
            self.logging.debug("Event with <ack_value> '%s' received but was not previously acknowledged." % (self.kwargs.ack_value))
