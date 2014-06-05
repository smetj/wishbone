#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  funnel.py
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
from wishbone.error import QueueFull


class Funnel(Actor):
    '''**Funnel multiple incoming queues to 1 outgoing queue.**

    Funnel multiple incoming queues to 1 outgoing queue.

    Parameters:

        - name(str):    The name of the module

        - size(int):    The size of all module queues.


    Queues:

        outbox:     Outgoing events.

    '''


    def __init__(self, name, size=100):

        Actor.__init__(self, name, size=size)
        self.name=name
        self.pool.createQueue("outbox")

    def preHook(self):

        for queue in self.pool.listQueues(default=False, names=True):
            if queue != "outbox":
                self.registerConsumer(self.consume, queue)

    def consume(self, event):

        self.submit(event, self.pool.queue.outbox)
