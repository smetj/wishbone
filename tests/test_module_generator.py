#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_generator.py
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


from wishbone.module.generator import Generator

from wishbone.actor import ActorConfig
from wishbone.queue import QueuePool
from wishbone.utils.test import getter


def test_module_generator_basic():

    actor_config = ActorConfig('generator', QueuePool())
    test_event = Generator(actor_config, payload="test")

    test_event.pool.queue.outbox.disableFallThrough()
    test_event.start()

    event = getter(test_event.pool.queue.outbox)
    assert event.get() == "test"


def test_module_generator_dict():

    actor_config = ActorConfig('generator', QueuePool())
    test_event = Generator(actor_config, payload={"one": 1})

    test_event.pool.queue.outbox.disableFallThrough()
    test_event.start()

    event = getter(test_event.pool.queue.outbox)
    assert event.get()["one"] == 1
