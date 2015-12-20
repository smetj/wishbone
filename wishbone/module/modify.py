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
import re
import csv


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

    def __init__(self, actor_config, expressions=[]):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        for expression in self.kwargs.expressions:
            command, args = self.__extractExpr(expression)
            event = getattr(self, "command%s" % (command))(event, *args)

        self.submit(event, self.pool.queue.outbox)

    def commandset(self, event, value, key):

        event.set(value, key)
        return event

    def commanddelete(self, event, key):

        event.delete(key)
        return event

    def __extractExpr(self, e):

        assert isinstance(e, dict)
        assert len(e.keys()) == 1

        c = e.keys()[0]
        assert c in ["set", "delete"]

        assert isinstance(e[c], list)
        return c, e[c]
