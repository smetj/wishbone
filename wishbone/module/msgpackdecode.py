#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  msgpackencode.py
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
import msgpack


class MSGPackDecode(Actor):

    '''**Decodes MSGPack data into Python objects.**

    Decodes the payload or complete events from MSGPack format.

    Parameters:

        - complete(bool)(False)
           |  When True encodes the complete event.  If False only
           |  encodes the data part.

    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, complete=False):
        Actor.__init__(self, actor_config)

        self.complete = complete
        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        if self.complete:
            self.decode = self.__decodeComplete
        else:
            self.decode = self.__decodeData

    def consume(self, event):
        event = self.decode(event)
        self.submit(event, self.pool.queue.outbox)

    def __decodeComplete(self, event):
        return msgpack.unpackb(event.data)

    def __decodeData(self, event):

        event.data = msgpack.unpackb(event.data)
        return event



