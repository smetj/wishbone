#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_loglevelfilter.py
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
from wishbone.module import LogLevelFilter
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty

from utils import getter

def test_module_loglevelfilter():

    actor_config = ActorConfig('loglevelfilter', 100, 1)
    loglevelfilter = LogLevelFilter(actor_config)
    loglevelfilter.pool.queue.inbox.disableFallThrough()
    loglevelfilter.pool.queue.outbox.disableFallThrough()
    loglevelfilter.start()

    e_one = Event('test')
    e_one.setData((7, 1367682301.430527, 3342, 'Router', 'Received SIGINT. Shutting down.'))

    e_two = Event('test')
    e_two.setData((1, 1367682301.430527, 3342, 'Router', 'Received SIGINT. Shutting down.'))


    loglevelfilter.pool.queue.inbox.put(e_one)
    loglevelfilter.pool.queue.inbox.put(e_two)

    one=getter(loglevelfilter.pool.queue.outbox)
    assert one.data == (1, 1367682301.430527, 3342, 'Router', 'Received SIGINT. Shutting down.')
    two=getter(loglevelfilter.pool.queue.outbox)
    assert two == None
