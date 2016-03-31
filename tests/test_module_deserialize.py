#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_deserialize.py
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
from wishbone.module.deserialize import Deserialize
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter


def test_module_deserialize_deserialize():

    actor_config = ActorConfig('deserialize', 100, 1, {}, "")
    deserialize = Deserialize(actor_config)

    deserialize.pool.queue.inbox.disableFallThrough()
    deserialize.pool.queue.outbox.disableFallThrough()
    deserialize.start()

    e = Event([{"one": 1}, {"two": 2}, {"three": 3}])

    deserialize.pool.queue.inbox.put(e)
    one = getter(deserialize.pool.queue.outbox)
    two = getter(deserialize.pool.queue.outbox)
    three = getter(deserialize.pool.queue.outbox)
    assert one.get() == {"one": 1}
    assert two.get() == {"two": 2}
    assert three.get() == {"three": 3}
    print three.dump(complete=True)
    assert three.get('@tmp.deserialize.generated_by') == True
