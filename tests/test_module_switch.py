#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_switch.py
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
from wishbone.module.switch import Switch
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter


def test_module_switch_default():

    actor_config = ActorConfig('switch', 100, 1, {}, "")

    switch = Switch(actor_config, outgoing="one")
    switch.pool.queue.inbox.disableFallThrough()
    switch.pool.queue.outbox.disableFallThrough()

    switch.pool.createQueue("one")
    switch.pool.queue.one.disableFallThrough()

    switch.start()

    event_one = Event("one")

    switch.pool.queue.inbox.put(event_one)

    assert getter(switch.pool.queue.one).get() == "one"

    switch.stop()

def test_module_switch_event():

    actor_config = ActorConfig('switch', 100, 1, {}, "")

    switch = Switch(actor_config, outgoing="one")
    switch.pool.queue.inbox.disableFallThrough()
    switch.pool.queue.outbox.disableFallThrough()

    switch.pool.createQueue("one")
    switch.pool.queue.one.disableFallThrough()

    switch.pool.createQueue("two")
    switch.pool.queue.two.disableFallThrough()

    switch.start()

    event_one = Event("one")
    switch.pool.queue.inbox.put(event_one)
    assert getter(switch.pool.queue.one).get() == "one"

    event_two = Event("two")
    switch_event = Event("two")

    switch.pool.queue.switch.put(switch_event)
    switch.pool.queue.inbox.put(event_two)

    assert getter(switch.pool.queue.two).get() == "two"

    switch.stop()
