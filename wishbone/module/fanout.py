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
from copy import deepcopy


class Fanout(Actor):

    '''**A builtin Wishbone module which duplicates incoming events to all
    connected queues.**

    Create a "1 to n" relationship with queues.  Events arriving in inbox
    are then copied to each queue connected to this module.  Keep in mind
    that the outbox queue is never used.

    When clone is True, each incoming event is duplicated for each outgoing
    queue.  This might be usefull if you require to change the content of the
    events later down the pipeline.  Otherwise references are used which means
    changing the event will change it everywhere in the current Wishbone
    framework.


    Parameters:

        name(str):      The name of the module.

        clone(bool):    When True actually makes a copy instead of passing
                        a reference.

    Queues:

        inbox:  Incoming events
    '''

    def __init__(self, name, clone=False):
        Actor.__init__(self, name, limit=0)
        if clone == False:
            self.consume = self.__consumeNoDeep
        else:
            self.consume = self.__consumeDeep

    def preHook(self):
        destination_queues = self.queuepool.getQueueInstances()
        del(destination_queues["inbox"])
        del(destination_queues["outbox"])
        self.destination_queues = [destination_queues[queue] for queue in destination_queues.keys()]

    def consume(self, event):
        for queue in self.destination_queues:
            queue.put(event)

    def __consumeNoDeep(self, event):
        for queue in self.destination_queues:
            queue.put(event)

    def __consumeDeep(self, event):
        for queue in self.destination_queues:
            queue.put(deepcopy(event))

