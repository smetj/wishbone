#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  uppercase.py
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


class Uppercase(ModuleFunction):
    '''
    Puts the desired field in uppercase.

    A Wishbone module function which converts the desired field to uppercase.

    Args:
        source (str): The source field
        destination (str): The destination field
    '''

    def __init__(self, source='data', destination='data'):

        self.source = source
        self.destination = destination

    def do(self, event):
        '''
        The function mapped to the module function.

        Args:
            event (wishbone.event.Event): The Wishbone event.

        Returns:
            wishbone.event.Event: The modified event.
        '''

        event.set(event.get(self.source).upper(), self.destination)
        return event
