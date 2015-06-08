#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  consensus.py
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


class Consensus(Actor):

    '''**For each incoming queue an event is expected prior generating a new event.**

    DESCRIPTION


    Parameters:

        - lookup(str)
           |  The lookup value.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, lookup):

        Actor.__init__(self, actor_config)
        self.pool.createQueue("outbox")
        self.__queue_slot = {}

    def preHook(self):

        for queue in self.pool.listQueues(default=False, names=True):
            if queue != "outbox":
                self.registerConsumer(self.generateConsume(queue), queue)

    def generateConsume(self, queue):
        self.__queue_slot[queue] = []

        def consume(event):
            if self.kwargs.lookup not in self.__queue_slot[queue]:
                self.__queue_slot[queue].append(self.kwargs.lookup)
                if self.consensusAchieved(self.kwargs.lookup):
                    self.submit(event, self.pool.queue.outbox)

        return consume

    def consensusAchieved(self, lookup):

        result = []
        for key, value in self.__queue_slot.iteritems():
            if lookup not in value:
                return False
        self.cleanup(lookup)
        return True

    def cleanup(self, lookup):

        for key, value in self.__queue_slot.iteritems():
            value.remove(lookup)