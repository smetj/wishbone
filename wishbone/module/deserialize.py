#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  deserialize.py
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


class Deserialize(Actor):

    '''**Creates new events from an array.**

    Takes an array and creates a new event out of each item of the array.

    Parameters:

        - source(str)("@data")
           |  The source of the array.

        - destination(str)("@data")
           |  The destination key to store the array item.

    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, source="@data", destination="@data"):

        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        data = event.get(self.kwargs.source)

        if isinstance(data, list):
            for item in data:
                e = event.clone()
                e.set(True, "@tmp.%s.generated_by" % (self.name))
                e.set("", self.kwargs.destination)
                e.set(item, self.kwargs.destination)
                self.submit(e, self.pool.queue.outbox)
        else:
            raise Exception("%s does not appear to contain an array." % (self.kwargs.source))
