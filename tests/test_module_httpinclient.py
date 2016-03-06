#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_httpinclient.py
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

from wishbone.module.httpinclient import HTTPInClient
from wishbone.actor import ActorConfig
from utils import getter
from gevent import sleep


def test_module_httpinclient():

    actor_config = ActorConfig('httpinclient', 100, 1, {}, "")
    http = HTTPInClient(actor_config, url="http://www.google.com", interval=1, allow_redirects=True)

    http.pool.queue.outbox.disableFallThrough()
    http.start()

    sleep(3)
    one = getter(http.pool.queue.outbox)
    assert "Google" in one.get()


def test_module_httpinclientTimeout():

    actor_config = ActorConfig('httpinclient', 100, 1, {}, "")
    http = HTTPInClient(actor_config, url="http://www.github.com", interval=1, allow_redirects=True, timeout=0.001)

    http.pool.queue.outbox.disableFallThrough()
    http.start()

    sleep(3)
    try:
        getter(http.pool.queue.failed)
    except Exception:
        assert True
    else:
        assert False
