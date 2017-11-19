#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_unpack.py
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


from wishbone.module.unpack import Unpack

from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
from wishbone.event import Event


def test_module_unpack():

    actor_config = ActorConfig('unpack', 100, 1, {}, "")
    unpack = Unpack(actor_config)

    unpack.pool.queue.inbox.disableFallThrough()
    unpack.pool.queue.outbox.disableFallThrough()
    unpack.start()

    bulk = Event(bulk=True)

    for _ in range(0, 10):
        bulk.appendBulk(Event())

    unpack.pool.queue.inbox.put(bulk)

    for _ in range(0, 10):
        assert getter(unpack.pool.queue.outbox)

    try:
        getter(unpack.pool.queue.outbox)
    except Exception:
        assert True
    else:
        assert False
