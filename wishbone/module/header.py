#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  header.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
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
from wishbone.errors import QueueFull, QueueLocked


class Header(Actor):
    '''** A builtin Wishbone module which adds the defined dictionary
    to the header of each passing event.**

    Parameters:

        - name(str):    The name of the module

        - header(dict): The dictionary to update the headers.
                        Default: {}

    Queues:

        - inbox:      Incoming events.

        - outbox:     Outgoing modified events.

    '''

    def __init__(self, name, header={}):
        Actor.__init__(self, name)
        self.header=header

    def consume(self, event):
        event["header"].update(self.header)
        try:
            self.queuepool.outbox.put(event)

        except (QueueFull, QueueLocked):
            self.queuepool.inbox.putLock()
            self.queuepool.inbox.rescue(event)
            self.queuepool.outbox.waitUntilPutAllowed()
            self.queuepool.inbox.putUnlock()