#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  roundrobin.py
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
from itertools import cycle
from random import randint


class RoundRobin(Actor):

    '''**Round-robins incoming events to all connected queues.**

    Create a "1 to n" relationship between queues.  Events arriving in inbox
    are then submitted in a roundrobin (or randomized) fashion to the
    connected queues.  The outbox queue is non existent.

    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - randomize(bool)(False)
            |  Randomizes the queue selection instead of going round-robin
            |  over all queues.


    Queues:

        - inbox
           |  Incoming events
    '''

    def __init__(self, name, size=100, frequency=1, randomize=False):
        Actor.__init__(self, name, size, frequency)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        self.randomize = randomize

    def preHook(self):

        self.destination_queues = []
        for queue in self.pool.listQueues(names=True):
            if queue not in ["admin_in", "admin_out", "failed", "success", "metrics", "logs"]:
                self.destination_queues.append(self.pool.getQueue(queue))

        if not self.randomize:
            self.cycle = cycle(self.destination_queues)
            self.chooseQueue = self.__chooseNextQueue
        else:
            self.chooseQueue = self.__chooseRandomQueue

    def consume(self, event):
        queue = self.chooseQueue()
        self.submit(event, queue)

    def __chooseNextQueue(self):
        return self.cycle.next()

    def __chooseRandomQueue(self):
        index = randint(0, len(self.destination_queues)-1)
        return self.destination_queues[index]