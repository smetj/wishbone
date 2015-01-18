#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_msgpackdecode.py
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
from wishbone.module import MSGPackDecode
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty

from utils import getter

def test_module_msgpackdecode():

    actor_config = ActorConfig('msgpackdecode', 100, 1)
    msgpackdecode = MSGPackDecode(actor_config)

    msgpackdecode.pool.queue.inbox.disableFallThrough()
    msgpackdecode.pool.queue.outbox.disableFallThrough()
    msgpackdecode.start()

    e = Event('test')
    e.setData('\x93\x01\x02\x03')

    msgpackdecode.pool.queue.inbox.put(e)
    one=getter(msgpackdecode.pool.queue.outbox)
    assert one.data == [1, 2, 3]