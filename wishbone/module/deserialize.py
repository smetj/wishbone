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
from wishbone.event import Bulk


class Deserialize(Actor):

    '''**Deserializes Bulk events or arrays.**

    When incoming data is a Bulk object the content will be forwarded as
    single events again.

    When the incoming data is a single and <source> is a list/array a new
    event is created from each element of the array.

    Parameters:

        - source(str)("@data")
           |  The source of the array.
           |  (Ignored when incoming type is Bulk)

        - destination(str)("@data")
           |  The destination key to store the array item.
           |  (Ignored when incoming type is Bulk)

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

        if isinstance(event, Bulk):
            for e in event.dump():
                self.submit(e, self.pool.queue.outbox)
            self.logging.debug("Expanded Bulk event into %s events." % (event.size()))
        else:
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
