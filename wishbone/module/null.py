#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  null.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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

from wishbone import Actor
from gevent import spawn, sleep


class Null(Actor):

    '''**Purges incoming events.**

    Purges incoming events.


    Parameters:

        - name(str):    The name of the module.

        - size(int):    The size of all module queues.


    Queues:

        - inbox:    incoming events
    '''

    def __init__(self, name, size=100):

        Actor.__init__(self, name, size=size)
        self.name = name
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):
        pass
