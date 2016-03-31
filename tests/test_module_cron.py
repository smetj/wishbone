#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_cron.py
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

from wishbone.module.cron import Cron
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter


def test_module_cron_default():

    actor_config = ActorConfig('cron', 100, 1, {}, "")
    cron = Cron(actor_config, '*/1 * * * *')
    cron.pool.queue.outbox.disableFallThrough()
    cron.start()

    one = getter(cron.pool.queue.outbox)
    cron.stop()

    assert one.get() == "wishbone"
