#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  jsonencode.py
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
from json import dumps


class JSONEncode(Actor):

    '''**Converts Python dict data structures to JSON strings.**

    Encodes Python data structures to JSON.


    Parameters:

        - source(str)("@data")
            | The data to convert.

        - destination(str)("@data")
            | The location to write the JSON string to.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, source='@data', destination='@data'):

        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        data = event.get(self.kwargs.source)
        data = dumps(data)
        event.set(data, self.kwargs.destination)
        self.submit(event, self.pool.queue.outbox)
