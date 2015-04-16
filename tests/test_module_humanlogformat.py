#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_humanlogformat.py
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
from wishbone.module import HumanLogFormat
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty
from utils import getter


def test_module_humanlogformat():

    actor_config = ActorConfig('humanlogformat', 100, 1, {})
    humanlogformat = HumanLogFormat(actor_config, colorize=False)
    humanlogformat.pool.queue.inbox.disableFallThrough()
    humanlogformat.pool.queue.outbox.disableFallThrough()
    humanlogformat.start()

    e = Event('test')
    e.setData((6, 1367682301.430527, 3342, 'Router', 'Received SIGINT. Shutting down.'))

    humanlogformat.pool.queue.inbox.put(e)
    one = getter(humanlogformat.pool.queue.outbox)
    assert one.data == "2013-05-04T17:45:01 setup.py[3342]: informational Router: Received SIGINT. Shutting down."