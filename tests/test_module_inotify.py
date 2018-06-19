#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_inotify.py
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

from wishbone.module.wb_inotify import WBInotify
from wishbone.actor import ActorConfig
from wishbone.queue import QueuePool
from wishbone.utils.test import getter
from uuid import uuid4
import os
from gevent import sleep


def test_module_inotify_default():

    # Standard situation.  Monitors the changes to a file.

    actor_config = ActorConfig('inotify', QueuePool())

    filename = "/tmp/%s" % str(uuid4())
    open(filename, 'a').close()

    inotify = WBInotify(actor_config, initial_listing=True, paths={filename: []})
    inotify.pool.queue.outbox.disableFallThrough()
    inotify.start()
    sleep(1)
    os.unlink(filename)
    sleep(1)
    e = getter(inotify.pool.queue.outbox)
    assert e.get() == {"path": filename, "inotify_type": "WISHBONE_INIT"}
    assert getter(inotify.pool.queue.outbox).get()["inotify_type"] == "IN_ATTRIB"
    assert getter(inotify.pool.queue.outbox).get()["inotify_type"] == "IN_DELETE_SELF"
