#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  binary.py
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

from wishbone.protocol import Encode


class Binary(Encode):

    '''
    Encodes a Python object into a binary representation.

    Parameters:

        n/a
    '''

    def __init__(self, charset='utf-8'):
        self.charset = charset

    def handleString(self, data):
        return data.encode(self.charset)
