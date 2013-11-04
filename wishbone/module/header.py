#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  header.py
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


class Header(Actor):
    '''** A builtin Wishbone module which adds the defined dictionary
    to the header of each passing event.**

    Parameters:

        - name(str):    The name of the module

        - key (str):    The header key to store the information.
                        Default: <name>

        - header(dict): The data to store.
                        Default: {}

        - expr(str):    printf-style String Formatting.
                        Expects event["data"] to be a dictionary.
                        the dictionary.
                        Default: None

    Queues:

        - inbox:      Incoming events.

        - outbox:     Outgoing modified events.

    '''

    def __init__(self, name, key=None, header={}, expr=None):
        Actor.__init__(self, name)
        if key == None:
            self.key=name
        else:
            self.key=key

        if expr == None:
            self.addHeader=self.__doPrintf
        else:
            self.addHeader=self.__doHeader

    def consume(self, event):
        event=self.addHeader(event)
        self.queuepool.outbox.put(event)

    def __doHeader(self, event):
        return event["header"][self.key]=self.header

    def __doPrintf(self, event):
        try:
            return self.expr%event["data"]
        except Exception as err:
            self.logging.error("String replace failed.  Reason: %s"%(err))
            return event
