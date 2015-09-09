#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  keyvalue.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
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


class KeyValue(Actor):

    '''**Adds the requested key values to the event data.**

    Assumes event.data is a Python datastructure to which the requested key
    values can be added. Otherwise event.data is moved to a key name "<body>".

    Existing keys will be overwritten.

    Parameters:

        - body(str)("data")
           |  If event.data is not a dict, replace by dict and copy event.data
           |  into event.data.<body>

        - overwrite(dict)({})
           |  A dict of key/value pairs to overwrite existing keys.

    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, actor_config, body="data", overwrite=[]):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        data = {}
        if not isinstance(event.data, dict):
            data[self.kwargs.body] = event.data
        else:
            data = event.data

        for key, value in self.kwargs.overwrite:
            data[key] = getattr(self.kwargs.overwrite, key)

            event.data = data
            self.submit(event, self.pool.queue.outbox)