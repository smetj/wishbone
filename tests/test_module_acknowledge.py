#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_acknowledge.py
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

from wishbone.event import Event
from wishbone.module.acknowledge import Acknowledge
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
from uplook import UpLook
from wishbone.lookup import EventLookup


def test_module_acknowledge_default():

    # Standard situation.  Event passes through as it's
    # the first time is is acknowledged.

    actor_config = ActorConfig('acknowledge', 100, 1, {}, "")
    acknowledge = Acknowledge(actor_config)
    acknowledge.pool.queue.inbox.disableFallThrough()
    acknowledge.pool.queue.outbox.disableFallThrough()
    acknowledge.pool.queue.acknowledge.disableFallThrough()
    acknowledge.pool.queue.dropped.disableFallThrough()

    acknowledge.start()
    event_one = Event("one")

    acknowledge.pool.queue.inbox.put(event_one)
    assert getter(acknowledge.pool.queue.outbox).get() == "one"
    acknowledge.stop()


def test_module_acknowledge_dropped():

    # An  event tries to pass through with an unacknowledged ack_id and
    # therefor should be dropped.

    actor_config = ActorConfig('acknowledge', 100, 1, {}, "")
    acknowledge = Acknowledge(actor_config)
    acknowledge.pool.queue.inbox.disableFallThrough()
    acknowledge.pool.queue.outbox.disableFallThrough()
    acknowledge.pool.queue.acknowledge.disableFallThrough()
    acknowledge.pool.queue.dropped.disableFallThrough()

    acknowledge.start()

    acknowledge.pool.queue.inbox.put(Event("one"))
    acknowledge.pool.queue.inbox.put(Event("one"))

    assert getter(acknowledge.pool.queue.dropped).get() == "one"
    acknowledge.stop()

def test_module_acknowledge_acknowledge():

    # An unacknowledged ack_id gets acknowledged and therefor lets then next
    # event with the same ack_id through.

    actor_config = ActorConfig('acknowledge', 100, 1, {}, "")
    acknowledge = Acknowledge(actor_config)
    acknowledge.pool.queue.inbox.disableFallThrough()
    acknowledge.pool.queue.outbox.disableFallThrough()
    acknowledge.pool.queue.acknowledge.disableFallThrough()
    acknowledge.pool.queue.dropped.disableFallThrough()

    acknowledge.start()

    event_one = Event("one")

    acknowledge.pool.queue.inbox.put(event_one)
    assert getter(acknowledge.pool.queue.outbox).get() == "one"
    acknowledge.pool.queue.acknowledge.put(event_one)
    acknowledge.pool.queue.inbox.put(event_one)
    assert getter(acknowledge.pool.queue.outbox).get() == "one"
    acknowledge.stop()

