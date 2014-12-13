#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_header.py
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
from wishbone.module import Header
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty

from utils import getter

def test_module_header():

    actor_config = ActorConfig('header', 100, 1)
    header = Header(actor_config, header={"greeting": "hello"})

    header.pool.queue.inbox.disableFallThrough()
    header.pool.queue.outbox.disableFallThrough()
    header.start()

    e = Event('test')
    e.setData('hello')

    header.pool.queue.inbox.put(e)
    one=getter(header.pool.queue.outbox)
    assert one.getHeaderValue("header", "greeting") == "hello"