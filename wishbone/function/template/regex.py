#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  regex.py
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
import re


class Regex(TemplateFunction):

    '''
    Regex matching on a string.


    A wishbone template function to do regex matching on strings.  Useful for
    conditional statements.

    Args:
        None
    '''

    def get(self, pattern, string):
        '''
        The function mapped to the template function.

        Args:
            pattern (str): The regex to apply.
            string (str): The data to evaluate.

        Returns:
            Bool: True if regex matches if not False
        '''

        if re.match(pattern, string):
            return True
        else:
            return False
