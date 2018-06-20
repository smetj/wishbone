#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_count.py
#
#  Copyright 2017 Jelle Smet <development@smetj.net>
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
from wishbone.module.count import Count
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
from wishbone.queue import QueuePool
from gevent import sleep


def test_module_count_default_pass():

    # Standard situation.  Event passes through after it appeared 10 times.

    conditions = {
        "data": {"value": "one", "occurrence": 10, "window": 60, "action": "pass"}
    }

    actor_config = ActorConfig("funnel", QueuePool(), disable_exception_handling=True)
    count = Count(actor_config, conditions)
    count.pool.queue.inbox.disableFallThrough()
    count.pool.queue.outbox.disableFallThrough()
    count.pool.queue.dropped.disableFallThrough()
    count.start()

    for _ in range(0, 9):
        count.pool.queue.inbox.put(Event("one"))
        result = getter(count.pool.queue.dropped).get()
        assert result == "one"

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.outbox).get() == "one"
    count.stop()


def test_module_count_timeout_pass():

    # Standard situation.  Event passes through after it appeared 10 times.

    conditions = {
        "data": {"value": "one", "occurrence": 3, "window": 2, "action": "pass"}
    }

    actor_config = ActorConfig("funnel", QueuePool(), disable_exception_handling=True)
    count = Count(actor_config, conditions)
    count.pool.queue.inbox.disableFallThrough()
    count.pool.queue.outbox.disableFallThrough()
    count.pool.queue.dropped.disableFallThrough()
    count.start()

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.dropped).get() == "one"

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.dropped).get() == "one"

    sleep(2)

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.dropped).get() == "one"

    count.stop()


def test_module_count_default_dropped():

    # Standard situation.  Events get dropped after it appeared 10 times.

    conditions = {
        "data": {"value": "one", "occurrence": 10, "window": 60, "action": "drop"}
    }

    actor_config = ActorConfig("funnel", QueuePool(), disable_exception_handling=True)
    count = Count(actor_config, conditions)
    count.pool.queue.inbox.disableFallThrough()
    count.pool.queue.outbox.disableFallThrough()
    count.pool.queue.dropped.disableFallThrough()
    count.start()

    for _ in range(0, 9):
        count.pool.queue.inbox.put(Event("one"))
        result = getter(count.pool.queue.outbox).get()
        assert result == "one"

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.dropped).get() == "one"
    count.stop()


def test_module_count_timeout_drop():

    conditions = {
        "data": {"value": "one", "occurrence": 3, "window": 2, "action": "drop"}
    }

    actor_config = ActorConfig("funnel", QueuePool(), disable_exception_handling=True)
    count = Count(actor_config, conditions)
    count.pool.queue.inbox.disableFallThrough()
    count.pool.queue.outbox.disableFallThrough()
    count.pool.queue.dropped.disableFallThrough()
    count.start()

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.outbox).get() == "one"

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.outbox).get() == "one"

    sleep(2)

    count.pool.queue.inbox.put(Event("one"))
    assert getter(count.pool.queue.outbox).get() == "one"

    count.stop()
