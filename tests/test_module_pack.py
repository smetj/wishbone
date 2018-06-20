#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_pack.py
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
from wishbone.module.pack import Pack
from wishbone.actor import ActorConfig
from wishbone.queue import QueuePool
from wishbone.utils.test import getter
from gevent import sleep


def test_module_pack_size():

    # Wraps  10 events into a bulk event.

    actor_config = ActorConfig("pack", QueuePool(), disable_exception_handling=True)
    bucket = Pack(actor_config, bucket_size=10)
    bucket.pool.queue.inbox.disableFallThrough()
    bucket.pool.queue.outbox.disableFallThrough()
    bucket.start()

    for c in range(0, 15):
        bucket.pool.queue.inbox.put(Event(c))

    b = getter(bucket.pool.queue.outbox)
    assert b.isBulk()
    assert len(b.data["data"]) == 10
    bucket.stop()


def test_module_pack_time():

    # Bucket spills in 1 second

    actor_config = ActorConfig("pack", QueuePool(), disable_exception_handling=True)
    bucket = Pack(actor_config, bucket_age=1)
    bucket.pool.queue.inbox.disableFallThrough()
    bucket.pool.queue.outbox.disableFallThrough()
    bucket.start()

    bucket.pool.queue.inbox.put(Event("hello"))
    sleep(1)
    b = getter(bucket.pool.queue.outbox)
    assert len(b.data["data"]) == 1
    bucket.stop()
