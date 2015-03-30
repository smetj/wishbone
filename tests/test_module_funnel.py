#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_funnel.py
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

import pytest

from wishbone.event import Event
from wishbone.module import Funnel
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty

from utils import getter


def test_module_funnel():

    actor_config = ActorConfig('funnel', 100, 1, {})
    funnel = Funnel(actor_config)
    funnel.pool.queue.outbox.disableFallThrough()

    funnel.pool.createQueue("one")
    funnel.pool.queue.one.disableFallThrough()

    funnel.pool.createQueue("two")
    funnel.pool.queue.two.disableFallThrough()

    funnel.start()

    event_one = Event("test")
    event_one.setData("one")

    event_two = Event("test")
    event_two.setData("two")

    funnel.pool.queue.one.put(event_one)
    funnel.pool.queue.two.put(event_two)

    assert getter(funnel.pool.queue.outbox).raw()["test"]["data"] == "one"
    assert getter(funnel.pool.queue.outbox).raw()["test"]["data"] == "two"

    funnel.stop()
