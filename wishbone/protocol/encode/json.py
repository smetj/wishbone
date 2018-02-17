#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  json.py
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
from json import dumps


class JSON(Encode):

    '''**Encode data into JSON format.**

    Convert a Python datastructure into JSON format.

    Parameters:

        - sort_keys(bool)(False)
            |  Sorts keys when True

        - ensure_ascii(bool)(False)
            |  When True makes sure all chars are valid ascii

        - ident(int)(None)
            |  The indentation used.

    '''

    def __init__(self, sort_keys=False, ensure_ascii=False, indent=None):
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii
        self.indent = indent

    def handleDict(self, data):
        return dumps(data, sort_keys=self.sort_keys, ensure_ascii=self.ensure_ascii, indent=self.indent)

    def handleCut(self, data):
        return self.handleDict(dict(data))

    handleList = handleDict
