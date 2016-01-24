#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  jq.py
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

from wishbone import Actor
from jq import jq


class JQ(Actor):

    '''**Evaluates a data structure against jq expressions.**

    Evalutes (JSON) data structures against a set of jq expressions to decide
    which queue to forward the event to.


    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - conditions(dict)([])
           |  A dictionary consisting out of expression, queue, payload.


    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, actor_config, selection="@data", conditions=[]):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        data = event.get(self.kwargs.selection)

        for condition in self.kwargs.conditions:
            if jq(condition["expression"]).transform(data):
                self.submit(event.clone(), self.pool.getQueue(condition["queue"]))
