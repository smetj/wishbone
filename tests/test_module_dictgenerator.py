#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_dictgenerator.py
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


from wishbone.module.dictgenerator import DictGenerator
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter


def test_module_dictgenerator_keys():

    actor_config = ActorConfig('template', 100, 1, {}, "")
    dictgenerator = DictGenerator(actor_config, keys=["one", "two"])

    dictgenerator.pool.queue.outbox.disableFallThrough()
    dictgenerator.start()

    event = getter(dictgenerator.pool.queue.outbox)

    assert "one" in event.get().keys()
    assert "two" in event.get().keys()


def test_module_dictgenerator_randomize_keys():

    actor_config = ActorConfig('template', 100, 1, {}, "")
    dictgenerator = DictGenerator(actor_config, randomize_keys=False)

    dictgenerator.pool.queue.outbox.disableFallThrough()
    dictgenerator.start()

    event = getter(dictgenerator.pool.queue.outbox)

    assert '0' in event.get().keys()


def test_module_dictgenerator_num_values():

    actor_config = ActorConfig('template', 100, 1, {}, "")
    dictgenerator = DictGenerator(actor_config, num_values=True, num_values_min=1, num_values_max=2)

    dictgenerator.pool.queue.outbox.disableFallThrough()
    dictgenerator.start()

    event = getter(dictgenerator.pool.queue.outbox)

    for key, value in event.get().iteritems():
        assert isinstance(value, int)

    assert isinstance(event.get().items()[0][1], int)
    assert event.get().items()[0][1] >= 1 and event.get().items()[0][1] <= 2


def test_module_dictgenerator_num_elements():

    actor_config = ActorConfig('template', 100, 1, {}, "")
    dictgenerator = DictGenerator(actor_config, min_elements=1, max_elements=2)

    dictgenerator.pool.queue.outbox.disableFallThrough()
    dictgenerator.start()

    event = getter(dictgenerator.pool.queue.outbox)

    assert len(event.get().keys()) >= 1 and len(event.get().keys()) <= 2
