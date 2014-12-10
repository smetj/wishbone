#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fanout.py
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


class Fanout(Actor):

    '''**Forward each incoming message to all connected queues.**

    Forward each incoming message to all connected queues.

    Parameters:

        - deep_copy(bool)(True)
           |  make sure that each incoming event is submitted
           |  to the outgoing queues as a seperate event and not a
           |  reference.


    Queues:

        inbox
         |  Outgoing events.

    '''

    def __init__(self, actor_config, deep_copy=True):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        self.destinations = []
        for queue in self.pool.listQueues(names=True, default=False):
            if queue != "inbox":
                self.destinations.append(self.pool.getQueue(queue))

        if self.deep_copy:
            self.copy = self.__doDeepCopy
        else:
            self.copy = self.__doNoDeepCopy

    def consume(self, event):

        for queue in self.destinations:
            self.submit(self.copy(event), queue)

    def __doDeepCopy(self, event):
        return event.clone()

    def __doNoDeepCopy(self, event):
        return event