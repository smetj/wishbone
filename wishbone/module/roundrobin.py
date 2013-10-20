#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  roundrobin.py
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
from itertools import cycle
from random import randint
from gevent import sleep

class RoundRobin(Actor):

    '''**A builtin Wishbone module which round robins incoming events
    over all connected queues.**

    Create a "1 to n" relationship between queues.  Events arriving in inbox
    are then submitted in a roundrobin (or randomized) fashion to the
    connected queues.  The outbox queue is non existent.


    Parameters:

        name(str):      The name of the module.

        randomize(bool):    Randomizes the queue selection instead of going
                            round robin over all queues.

    Queues:

        inbox:  Incoming events
    '''

    def __init__(self, name, randomize=False):
        Actor.__init__(self, name)
        self.deleteQueue("outbox")
        self.randomize=randomize

    def preHook(self):
        destination_queues = self.queuepool.getQueueInstances()
        del(destination_queues["inbox"])

        self.destination_queues = [destination_queues[queue] for queue in destination_queues.keys()]

        if self.randomize == False:
            self.cycle = cycle(self.destination_queues)
            self.chooseQueue=self.__chooseNextQueue
        else:
            self.chooseQueue=self.__chooseRandomQueue

    def consume(self, event):
        while self.loop():
            queue = self.chooseQueue()
            try:
                queue.put(event)
                break
            except:
                sleep()

    def __chooseNextQueue(self):
        return self.cycle.next()

    def __chooseRandomQueue(self):
        index = randint(0, len(self.destination_queues)-1)
        return self.destination_queues[index]
