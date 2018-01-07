#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  version.py
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
from pkg_resources import get_distribution


class Version(TemplateFunction):
    '''
    Returns the version of the desired Python module.

    A Wishbone template function wich returns the version a the defined Python
    module.

    Args:
        None
    '''

    def get(self, module="wishbone"):
        '''
        The function mapped to the template function.

        Args:
            module (str): The module name

        Returns:
            str: The version string
        '''

        return get_distribution(module).version
