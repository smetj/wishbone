#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  importing.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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


class TestImport():
    '''py.test tests dealing with importing various parts of
    wishbone'''

    def testWishbone(self):
        try:
            import wishbone
        except:
            assert wishbone

    def testWishboneBootstrap(self):
        try:
            from wishbone.bootstrap import PidHandling
        except:
            assert PidHandling

        try:
            from wishbone.bootstrap import ModuleHandling
        except:
            assert ModuleHandling

        try:
            from wishbone.bootstrap import Initialize
        except:
            assert Initialize

        try:
            from wishbone.bootstrap import Start
        except:
            assert Start

        try:
            from wishbone.bootstrap import Debug
        except:
            assert Debug

        try:
            from wishbone.bootstrap import Stop
        except:
            assert Stop

        try:
            from wishbone.bootstrap import Kill
        except:
            assert Kill

        try:
            from wishbone.bootstrap import List
        except:
            assert List

        try:
            from wishbone.bootstrap import Show
        except:
            assert Show

        try:
            from wishbone.bootstrap import Dispatch
        except:
            assert Dispatch

        try:
            from wishbone.bootstrap import BootStrap
        except:
            assert BootStrap

    def testWishboneErrors(self):

        try:
            from wishbone.errors import QueueEmpty
        except:
            assert QueueEmpty

        try:
            from wishbone.errors import QueueFull
        except:
            assert QueueFull

        try:
            from wishbone.errors import QueueLocked
        except:
            assert QueueLocked

        try:
            from wishbone.errors import QueueMissing
        except:
            assert QueueMissing

        try:
            from wishbone.errors import QueueOccupied
        except:
            assert QueueOccupied

        try:
            from wishbone.errors import SetupError
        except:
            assert SetupError

    def testWishboneModule(self):

        try:
            from wishbone.module import Fanout
        except:
            assert Fanout

        try:
            from wishbone.module import Funnel
        except:
            assert Funnel

        try:
            from wishbone.module import Graphite
        except:
            assert Graphite

        try:
            from wishbone.module import Header
        except:
            assert Header

        try:
            from wishbone.module import HumanLogFormatter
        except:
            assert HumanLogFormatter

        try:
            from wishbone.module import LockBuffer
        except:
            assert LockBuffer

        try:
            from wishbone.module import Null
        except:
            assert Null

        try:
            from wishbone.module import RoundRobin
        except:
            assert RoundRobin

        try:
            from wishbone.module import STDOUT
        except:
            assert STDOUT

        try:
            from wishbone.module import TestEvent
        except:
            assert TestEvent

        try:
            from wishbone.module import TippingBucket
        except:
            assert TippingBucket

        try:
            from wishbone.module import Syslog
        except:
            assert Syslog

    def testWishboneRouter(self):
        try:
            from wishbone.router import Default
        except:
            assert Default

    def testWishboneTools(self):

        try:
            from wishbone.tools import QueueFunctions
        except:
            assert QueueFunctions

        try:
            from wishbone.tools import LoopContextSwitcher
        except:
            assert LoopContextSwitcher

        try:
            from wishbone.tools import Consumer
        except:
            assert Consumer

        try:
            from wishbone.tools import QLogging
        except:
            assert QLogging

        try:
            from wishbone.tools import QueuePool
        except:
            assert QueuePool

        try:
            from wishbone.tools import Measure
        except:
            assert Measure

