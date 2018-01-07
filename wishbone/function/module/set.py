#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  set.py
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


class Set(ModuleFunction):
    '''
    Sets a field to the desired value.

    A Wishbone module function which sets data to the desired field.  Data can be a template.

    Args:
        data (str): The value (or template) to apply.
        destination (str): The destination field
    '''

    def __init__(self, data, destination='data'):

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

        if isinstance(self.data, str):
            data = event.render(self.data)
        else:
            data = self.data

        event.set(data, self.destination)

        return event
