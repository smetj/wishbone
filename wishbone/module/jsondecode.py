#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  jsondecode.py
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
from json import loads


class JSONDecode(Actor):

    '''**Decodes JSON data to Python data objects.**

    Decodes the payload or complete events from JSON format.

    Parameters:

        - source(str)("@data")
           |  The source of the event to decode.
           |  Use an empty string to refer to the complete event.

        - destination(str)("@data")
           |  The destination key to store the Python <dict>.
           |  Use an empty string to refer to the complete event.

        - unicode(bool)(True)
           |  When True, converts strings to unicode otherwise regular string.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, source="@data", destination="@data", str=True):

        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        if self.kwargs.str:
            self.convert = self.doUnicode
        else:
            self.convert = self.doNoUnicode

    def consume(self, event):

        data = event.get(self.kwargs.source)
        data = self.convert(data)
        event.set(data, self.kwargs.destination)
        self.submit(event, self.pool.queue.outbox)

    def doUnicode(self, data):
        return loads(data)

    def doNoUnicode(self, data):
        return self.json_loads_byteified(data)

    def json_loads_byteified(self, json_text):
        return self._byteify(
            loads(json_text, object_hook=self._byteify),
            ignore_dicts=True
        )

    def _byteify(self, data, ignore_dicts=False):
        # if this is a unicode string, return its string representation
        if isinstance(data, str):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [ self._byteify(item, ignore_dicts=True) for item in data ]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return {
                self._byteify(key, ignore_dicts=True): self._byteify(value, ignore_dicts=True)
                for key, value in list(data.items())
            }
        # if it's anything else, return it in its original form
        return data
