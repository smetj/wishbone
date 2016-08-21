#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cycle.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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

from wishbone.lookup import Lookup
from itertools import cycle as cycle_array


class Cycle(Lookup):

    '''
    **Cycles through the provided array returning the next element.**

    This function rotates through the elements in the provided array always
    returning the next element.  The order is fixed and when the end is
    reached the first element is returned again.

    - Parameters to initialize the function:

        - values(list)(None): An array of elements to cycle through/

    - Parameters to call the function:

        None
    '''

    def __init__(self, values):

        self.c = cycle_array(values)

    def lookup(self):

        return next(self.c)
