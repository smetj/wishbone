#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  unpack.py
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

from wishbone.module import ProcessModule
from wishbone.actor import Actor
from wishbone.event import Event
from wishbone.error import InvalidData


class Unpack(ProcessModule):

    '''**Unpacks bulk events into single events.**

    Creates single events from all the events stored in a bulk event.


    Parameters::

        None

    Queues::

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messages

        - dropped
           |  Dropped messages
    '''

    def __init__(self, actor_config):

        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("dropped")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):
        if event.isBulk():
            for e in event.dump()["data"]:
                try:
                    self.submit(Event().slurp(e), "outbox")
                except InvalidData:
                    self.logging.debug("Bulk event with id '%s' contained an invalid event. Invalid event skipped." % (event.get('uuid')))
            self.logging.debug("Expanded Bulk event into %s events." % (len(event.data)))
        else:
            self.logging.debug("Event with id '%s' is not a bulk event. Dropped.")
            self.submit(event, "dropped")
