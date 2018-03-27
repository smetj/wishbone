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
from wishbone.module import InputModule, OutputModule
from wishbone.error import ModuleInitFailure
from wishbone.protocol.decode.plain import Plain


class DummyModule(InputModule):

    def __init__(self, actor_config, native_events=False, destination="data"):
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
    assert d.decode.__self__.__class__.__name__ == "Dummy"


def test_module_override_protocol():

    actor_config = ActorConfig('DummyTest', 100, 1, {}, "", protocol=lambda: Plain().handler)
    d = DummyModule(actor_config)
    d.start()

    assert d.decode.__self__.__class__.__name__ == "Plain"


def test_init_inputmodule_good():

    class InputModuleTestGood(InputModule):

        def __init__(self, actor_config, native_events=False, destination="data"):
            InputModule.__init__(self, actor_config)

    actor_config = ActorConfig('DummyTest', 100, 1, {}, "")

    try:
        InputModuleTestGood(actor_config)
    except ModuleInitFailure:
        assert False
    else:
        assert True


def test_init_inputmodule_bad():

    class InputModuleTestBad_1(InputModule):

        def __init__(self, actor_config, destination=None):
            InputModule.__init__(self, actor_config)

    class InputModuleTestBad_2(InputModule):

        def __init__(self, actor_config, native_events=None):
            InputModule.__init__(self, actor_config)

    actor_config = ActorConfig('DummyTest', 100, 1, {}, "")

    for i in range(1, 3):
        try:
            locals()["InputModuleTestBad_%s" % (i)](actor_config)
        except ModuleInitFailure:
            assert True
        else:
            assert False


def test_init_outputmodule_good():

    class OutputModuleTestGood(OutputModule):
        def __init__(self, actor_config, selection=None, payload=None, native_events=None, parallel_streams=1):
            InputModule.__init__(self, actor_config)

    actor_config = ActorConfig('DummyTest', 100, 1, {}, "")

    try:
        OutputModuleTestGood(actor_config)
    except ModuleInitFailure:
        assert False
    else:
        assert True


def test_init_outputmodule_bad():

    class OutputModuleTestBad_1(OutputModule):
        def __init__(self, actor_config, payload=None, native_events=None, parallel_streams=1):
            InputModule.__init__(self, actor_config)

    class OutputModuleTestBad_2(OutputModule):
        def __init__(self, actor_config, selection=None, native_events=None, parallel_streams=1):
            InputModule.__init__(self, actor_config)

    class OutputModuleTestBad_3(OutputModule):
        def __init__(self, actor_config, selection=None, payload=None, parallel_streams=1):
            InputModule.__init__(self, actor_config)

    class OutputModuleTestBad_4(OutputModule):
        def __init__(self, actor_config, selection=None, payload=None, native_events=None):
            InputModule.__init__(self, actor_config)

    actor_config = ActorConfig('DummyTest', 100, 1, {}, "")

    for i in range(1, 5):
        try:
            locals()["OutputModuleTestBad_%s" % (i)](actor_config)
        except ModuleInitFailure:
            assert True
        else:
            assert False
