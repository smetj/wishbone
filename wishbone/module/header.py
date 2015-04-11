#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  header.py
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


class Header(Actor):

    '''**Adds information to event headers.**


    Parameters:

        - namespace(str)(None)
           |  The namespace to write the header to.
           |  <None> means self.name

        - header(dict)({})
           |  The data to store.

        - expr(str)(None)
           |  printf-style String Formatting.
           |  Expects event.data to be a dictionary.


    Queues:

        - inbox
           |  Incoming events.

        - outbox
           |  Outgoing events.
    '''

    def __init__(self, actor_config, namespace=None, header={}, expr=None):
        Actor.__init__(self, actor_config)

        if namespace is None:
            self.kwargs.namespace = self.name

        if self.kwargs.expr is None:
            self.addHeader = self.__doHeader
        else:
            self.addHeader = self.__doPrintf

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):
        event = self.addHeader(event)
        self.submit(event, self.pool.queue.outbox)

    def __doHeader(self, event):
        for key in self.kwargs.header:
            event.setHeaderValue(key, self.kwargs.header[key], self.kwargs.namespace)
        return event

    def __doPrintf(self, event):
        try:
            return self.kwargs.expr % event.data
        except Exception as err:
            self.logging.error("String replace failed.  Reason: %s" % (err))
            return event
