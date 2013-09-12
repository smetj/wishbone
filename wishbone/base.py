#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  base.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
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

from wishbone.tools import QueueFunctions
from wishbone.tools import QLogging
from wishbone.tools import Consumer

class BaseActor(QueueFunctions):
    def __init__(self, name):
        self.name=name
        QueueFunctions.__init__(self)
        self.logging=QLogging(name)
        self.logging.info("Initiated")

class Actor(BaseActor, Consumer):
    '''**This baseclass provides the functionality required to build a Wishbone module**

        Parameters:

            - name(string):         The name of the module.

            - setupbasic(bool):     When True, does some assumptions on how to setup the module.
                                    Default: True

            - context_switch(int):  Execute a context switch every <context_switch> messages
                                    consumed from a queue.
                                    Default: 100

            - limit(int):           When more than 0 the <consume> function is executed in a
                                    greenthread allowing parallel execution for each incoming
                                    event.  A threadpool of size <limit> is used to limit the
                                    number of parallel greenthreads.
                                    Default: 0

    '''
    def __init__(self, name,  setupbasic=True, context_switch=100, limit=0):
        BaseActor.__init__(self, name)
        Consumer.__init__(self, setupbasic=setupbasic, context_switch=context_switch, limit=limit)

    def enableThrottling(self):
        '''Should be overridden by the module author when throttling
        functionality is desired.

        This module is executed by the router whenever it detects this module
        is overflowing one of its children. '''

        self.logging.debug("Requested to enable throttling but no function overrides the default one.")

    def disableThrottling(self):
        '''Should be overridden by the module author when throttling
        functionality is desired.

        This module is executed by the router decides previously enabled
        throttling on this module can be disabled.'''

        self.logging.debug("Requested to disiable throttling but no function overrides the default one.")