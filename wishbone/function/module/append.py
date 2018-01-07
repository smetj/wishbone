#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  append.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from wishbone.function.module import ModuleFunction


class Append(ModuleFunction):
    '''
    Adds a value to an existing list.

    A Wishbone module function which add a value to an existing list.

    Args:
        data (str/int/float/list/dict): The data to add
        destination (str): The field to add data to.
    '''

    def __init__(self, data, destination='tags'):

        self.data = data
        self.destination = destination

    def do(self, event):
        '''
        The function mapped to the module function.

        Args:
            event (wishbone.event.Event): The Wishbone event.

        Returns:
            wishbone.event.Event: The modified event.
        '''

        if isinstance(self.data, (int, float, str)):
            lst = event.get(self.destination)
            if isinstance(lst, list):
                lst.append(self.data)
                event.set(lst, self.destination)
            else:
                raise Exception("'%s' is not an array" % (self.destination))
        else:
            raise Exception("'%s' is not a number or string." % (self.data))
        return event
