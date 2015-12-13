#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  modify.py
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


class Modify(Actor):

    '''**Modify and manipulate datastructures.**

    This module modifies the data of an event.


    Parameters:

        - set(dict)({})
           |  Sets the keys to the requested values

        - template(dict)({})
           |  Sets the keys to the requested values


    Queues:

        - outbox
           |  Contains the generated events.
    '''

    def __init__(self, actor_config, set={}, template={}):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        for key, value in self.kwargs.set:
            event.set(value, key)

        for key, value in self.kwargs.template:
            try:
                event.set(value.format(**event.raw()), key)
            except KeyError:
                event.set(value, key)

        self.submit(event, self.pool.queue.outbox)
