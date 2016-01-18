#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_loglevelfilter.py
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
from wishbone.event import Log
from wishbone.module.loglevelfilter import LogLevelFilter
from wishbone.actor import ActorConfig
from utils import getter


def test_module_loglevelfilter():

    actor_config = ActorConfig('loglevelfilter', 100, 1, {}, "")
    loglevelfilter = LogLevelFilter(actor_config)
    loglevelfilter.pool.queue.inbox.disableFallThrough()
    loglevelfilter.pool.queue.outbox.disableFallThrough()
    loglevelfilter.start()


    e_one = Event(Log(1367682301.430527, 7, 3342, 'Router', 'Received SIGINT. Shutting down.'))
    e_two = Event(Log(1367682301.430527, 1, 3342, 'Router', 'Received SIGINT. Shutting down.'))

    loglevelfilter.pool.queue.inbox.put(e_one)
    loglevelfilter.pool.queue.inbox.put(e_two)

    one = getter(loglevelfilter.pool.queue.outbox)
    assert one.get().time == 1367682301.430527
    try:
        getter(loglevelfilter.pool.queue.outbox)
    except Exception:
        assert True
    else:
        assert False
