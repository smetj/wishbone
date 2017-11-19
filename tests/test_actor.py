#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_actor.py
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

from wishbone.actorconfig import ActorConfig
from wishbone.module import InputModule


class DummyModule(InputModule):

    def __init__(self, actor_config):
        InputModule.__init__(self, actor_config)
        self.pool.createQueue("outbox")
        self.sendToBackground(self.producer)

    def producer(self):

        while self.loop():
            e = self.generateEvent("hello")
            self.submitEvent(e, "outbox")


def test_module():

    actor_config = ActorConfig('DummyTest', 100, 1, {}, "")
    d = DummyModule(actor_config)
    d.start()
    assert d.decode.__self__.__class__.__name__ == "DummyModule"
