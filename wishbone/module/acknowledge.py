#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  acknowledge.py
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

from wishbone.module import FlowModule
from gevent.lock import Semaphore
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


class Acknowledge(FlowModule):

    '''**Forwards or drops events by acknowleding values.**

    This module stores the value of field ``ack_id`` from each incoming event.
    Subsequent events with the same ``ack_id`` field value will be dropped
    until it is removed by having it acknowledged.

    The ``ack_id`` can be acknowledged by sending the event to the
    ``acknowledge`` queue.

    The ``ack_id`` field value should be an unique value.

    Typically, downstream modules's ``successful`` and/or ``failed`` queues are
    sending events to the ``acknowledge`` queue.


    Parameters::

        - ack_id (data):
            A unique value identifying the event.

    Queues::

        - inbox
            |  Incoming events

        - outbox
            |  Outgoing events

        - acknowledge
            |  Acknowledge events

        - dropped
            |  Where events go to when unacknowledged


    Event variables::

        - tmp.<name>.ack_id
            | The location of the acknowledgement ID when coming in through the
            | inbox queue.
    '''

    def __init__(self, actor_config, ack_id=None):
        FlowModule.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("acknowledge")
        self.pool.createQueue("dropped")
        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.acknowledge, "acknowledge")

        self.ack_table = AckList()

    def consume(self, event):

        if self.kwargs.ack_id is None:
            ack_id = self.generateID()
        else:
            ack_id = event.kwargs.ack_id

        if event.has("tmp.%s.ack_id" % (self.name)):
            self.logging.warning("Event arriving to <inbox> with tmp.%s.ack_id already set.  Perhaps that should have been the <acknowledge> queue instead." % (self.name))
        else:
            event.set({"ack_id": ack_id}, "tmp.%s" % (self.name))
            if self.ack_table.unack(ack_id):
                self.submit(event, "outbox")
            else:
                self.logging.debug("Event with still unacknowledged <ack_id> '%s' send to <dropped> queue." % (ack_id))
                self.submit(event, "dropped")

    def acknowledge(self, event):

        if event.has("tmp.%s.ack_id" % (self.name)):
            ack_id = event.get('tmp.%s.ack_id' % (self.name))
            if self.ack_table.ack(ack_id):
                self.logging.debug("Event acknowledged with <ack_id> '%s'." % (ack_id))
                event.delete('tmp.%s.ack_id' % (self.name))
            else:
                self.logging.debug("Event with <ack_id> '%s' received but was not previously acknowledged." % (ack_id))
        else:
            self.logging.warning("Received event without 'tmp.%s.ack_id' therefor it is dropped" % (self.name))

    def generateID(self):

        return ''.join(SystemRandom().choice(string.ascii_lowercase) for _ in range(4))

    def postHook(self):

        self.logging.debug("The ack table has %s events unacknowledged." % (len(self.ack_table.ack_table)))
