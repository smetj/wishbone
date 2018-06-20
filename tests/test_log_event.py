#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_log_event.py
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

from wishbone.module.generator import Generator
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
from wishbone.queue import QueuePool


def test_module_logs():

    actor_config = ActorConfig("generator", QueuePool())

    # {"time": time(), "level": level, "pid": getpid(), "module": self.name, "message": message}
    test_event = Generator(actor_config)
    test_event.pool.queue._logs.disableFallThrough()
    test_event.start()

    log = getter(test_event.pool.queue._logs).get()
    for key in ["time", "level", "pid", "module", "message"]:
        assert key in log
    test_event.stop()
