#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_jsondecode.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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
from wishbone.module import JSONDecode
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty

from utils import getter

def test_module_jsondecode():

    actor_config = ActorConfig('jsondecode', 100, 1)
    jsondecode = JSONDecode(actor_config)

    jsondecode.pool.queue.inbox.disableFallThrough()
    jsondecode.pool.queue.outbox.disableFallThrough()
    jsondecode.start()

    e = Event('test')
    e.setData('["one", "two", "three"]')

    jsondecode.pool.queue.inbox.put(e)
    one=getter(jsondecode.pool.queue.outbox)
    assert one.data == ["one", "two", "three"]