#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_fresh.py
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
from wishbone.module.fresh import Fresh
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
from gevent import sleep


def test_module_fresh_default():

    actor_config = ActorConfig('fresh', 100, 1, {}, "")
    fresh = Fresh(actor_config)
    fresh.pool.queue.inbox.disableFallThrough()
    fresh.pool.queue.outbox.disableFallThrough()
    fresh.pool.queue.timeout.disableFallThrough()

    fresh.start()

    e = Event("hello")

    fresh.pool.queue.inbox.put(e)
    one = getter(fresh.pool.queue.outbox)
    fresh.stop()

    assert one.get() == "hello"


def test_module_fresh_timeout():

    actor_config = ActorConfig('fresh', 100, 1, {}, "")
    fresh = Fresh(actor_config, timeout=1)
    fresh.pool.queue.inbox.disableFallThrough()
    fresh.pool.queue.outbox.disableFallThrough()
    fresh.pool.queue.timeout.disableFallThrough()

    fresh.start()
    sleep(2)
    one = getter(fresh.pool.queue.timeout)
    fresh.stop()

    assert one.get() == "timeout"

def test_module_fresh_recovery():

    actor_config = ActorConfig('fresh', 100, 1, {}, "")
    fresh = Fresh(actor_config, timeout=1)
    fresh.pool.queue.inbox.disableFallThrough()
    fresh.pool.queue.outbox.disableFallThrough()
    fresh.pool.queue.timeout.disableFallThrough()

    fresh.start()
    sleep(1)
    one = getter(fresh.pool.queue.timeout)
    event = Event("test")
    fresh.pool.queue.inbox.put(event)
    sleep(1)
    two = getter(fresh.pool.queue.timeout)
    fresh.stop()

    assert two.get() == "recovery"

def test_module_fresh_repeat():

    actor_config = ActorConfig('fresh', 100, 1, {}, "")
    fresh = Fresh(actor_config, timeout=1, repeat_interval=1)
    fresh.pool.queue.inbox.disableFallThrough()
    fresh.pool.queue.outbox.disableFallThrough()
    fresh.pool.queue.timeout.disableFallThrough()

    fresh.start()
    sleep(1)
    getter(fresh.pool.queue.timeout)
    sleep(1.5)
    one = getter(fresh.pool.queue.timeout)
    fresh.stop()

    assert one.get() == "timeout"

