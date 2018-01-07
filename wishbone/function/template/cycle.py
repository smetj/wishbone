#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cycle.py
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

from wishbone.function.template import TemplateFunction
from itertools import cycle as cycle_array


class Cycle(TemplateFunction):
    '''
    Cycles through the provided array returning the next element.

    A Wishbone template function which returns the next value of an array.

    This function rotates through the elements in the provided array always
    returning the next element.  The order is fixed and when the end is
    reached the first element is returned again.

    Args:

        values(list): A list of elements to cycle through.
    '''

    def __init__(self, values):

        self.c = cycle_array(values)

    def get(self):
        '''
        The function mapped to the template function.

        Args:
            None

        Returns:
            obj: An element of the provided array.
        '''

        return next(self.c)
