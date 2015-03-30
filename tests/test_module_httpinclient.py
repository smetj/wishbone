#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_httpinclient.py
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
from wishbone.module import HTTPInClient
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty
from utils import getter


def test_module_jsonencode():

    actor_config = ActorConfig('jsonencode', 100, 1, {})
    http = HTTPInClient(actor_config, url="http://www.google.com", interval=1)

    http.pool.queue.outbox.disableFallThrough()
    http.start()

    one = getter(http.pool.queue.outbox)
    print one.data
    assert "Google" in one.data
