#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_templating.py
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
from wishbone.componentmanager import ComponentManager

from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
from os import getpid


def test_templating_string():

    f = ComponentManager().getComponentByName("wishbone.function.template.pid")
    f_instance = f()
    actor_config = ActorConfig('generator', 100, 1, {"pid": f_instance}, "", disable_exception_handling=True)
    test_event = Generator(actor_config, payload="{{pid()}}")

    test_event.pool.queue.outbox.disableFallThrough()
    test_event.start()

    event = getter(test_event.pool.queue.outbox)
    assert event.get() == str(getpid())


def test_templating_list():

    f = ComponentManager().getComponentByName("wishbone.function.template.pid")
    f_instance = f()
    actor_config = ActorConfig('generator', 100, 1, {"pid": f_instance}, "", disable_exception_handling=True)
    test_event = Generator(actor_config, payload=["{{pid()}}"])

    test_event.pool.queue.outbox.disableFallThrough()
    test_event.start()

    event = getter(test_event.pool.queue.outbox)
    assert event.get()[0] == str(getpid())


def test_templating_dict():

    f = ComponentManager().getComponentByName("wishbone.function.template.pid")
    f_instance = f()
    actor_config = ActorConfig('generator', 100, 1, {"pid": f_instance}, "", disable_exception_handling=True)
    test_event = Generator(actor_config, payload={"one": "{{pid()}}"})

    test_event.pool.queue.outbox.disableFallThrough()
    test_event.start()

    event = getter(test_event.pool.queue.outbox)
    assert event.get()["one"] == str(getpid())


def test_templating_dict_in_list():

    f = ComponentManager().getComponentByName("wishbone.function.template.pid")
    f_instance = f()
    actor_config = ActorConfig('generator', 100, 1, {"pid": f_instance}, "", disable_exception_handling=True)
    test_event = Generator(actor_config, payload=[{"one": "{{pid()}}"}])

    test_event.pool.queue.outbox.disableFallThrough()
    test_event.start()

    event = getter(test_event.pool.queue.outbox)
    assert event.get()[0]["one"] == str(getpid())
