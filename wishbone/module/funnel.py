#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  funel.py
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


class Funnel(Actor):
    '''**Merges incoming events from multiple queues to 1 queue.**

    Create a "n to 1" relationship with queues.  Events arriving in different
    queues are all merged into the outbox.

    Parameters:

        name(str):  The name of the module

    Queues:

        outbox:     Outgoing events.

    '''

    def __init__(self, name):
        Actor.__init__(self, name)

    def preHook(self):
        source_queues = self.queuepool.getQueueInstances()
        del(source_queues["inbox"])
        del(source_queues["outbox"])
        self.source_queues = [source_queues[queue] for queue in source_queues.keys()]
        for queue in self.source_queues:
            self.registerConsumer(self.consume, queue)

    def consume(self, event):
        try:
            self.queuepool.outbox.put(event)
        except:
            self.queuepool.inbox.putLock()
            self.queuepool.inbox.rescue(event)
            self.queuepool.outbox.waitUntilPutAllowed()
