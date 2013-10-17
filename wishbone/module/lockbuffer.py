#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       lockbuffer.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone import Actor

class LockBuffer(Actor):
    '''**A builtin Wishbone module with a fixed size inbox queue.**

    This module shovels events from inbox to outbox.  The
    inbox however is fixed in size which locks the downstream
    modules when it reached its limit.

    Parameters:

        - name (str):   The instance name when initiated.

        - size (int):   The maximum size of inbox.
                        Default: 100

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    def __init__(self, name, size=100):
        Actor.__init__(self, name, setupbasic=False)
        self.createQueue("inbox", size)
        self.createQueue("outbox")
        self.registerConsumer(self.consume, self.queuepool.inbox)

    def consume(self,event):
        self.queuepool.outbox.put(event)