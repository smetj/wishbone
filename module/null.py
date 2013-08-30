#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  null.py
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


class Null(Actor):
    '''**Accepts events and purges these without any further processing.**

    Useful to discard a stream of events.

    Parameters:

        - name(str):  The name of the module


    Queues:

        - inbox:    incoming events
    '''

    def __init__(self, name):
        Actor.__init__(self, name, limit=0)

    def consume(self, event):
        pass
