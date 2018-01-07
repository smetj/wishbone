#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  funnel.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from wishbone.module import FlowModule


class Funnel(FlowModule):

    '''**Funnel multiple incoming queues to one outgoing queue.**

    Funnel multiple incoming queues to one outgoing queue.

    Parameters::

        n/a

    Queues::

        - outbox:
           |  Outgoing messages

    '''

    def __init__(self, actor_config):

        FlowModule.__init__(self, actor_config)
        self.pool.createQueue("outbox")

    def preHook(self):

        for queue in self.pool.listQueues(default=False, names=True):
            if queue != "outbox":
                self.registerConsumer(self.consume, queue)

    def consume(self, event):

        self.submit(event, "outbox")
