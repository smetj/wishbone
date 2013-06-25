#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  fanout.py
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


class Fanout(Actor):

    '''**A builtin Wishbone module which duplicates incoming events to all
    connected queues.**

    Queues can only have a 1 to 1 relationship.  If events have to go from
    1 to many queues, the Fanout module might be helpful.

    Parameters:

        name(str):  The name of the module

    Queues:

        inbox:  Incoming events
    '''

    def __init__(self, name):
        Actor.__init__(self, name, limit=0)

    def preHook(self):
        destination_queues = self.queuepool.getQueueInstances()
        del(destination_queues["inbox"])
        del(destination_queues["outbox"])
        self.destination_queues = [destination_queues[queue] for queue in destination_queues.keys()]

    def consume(self, event):
        for queue in self.destination_queues:
            queue.put(event)
