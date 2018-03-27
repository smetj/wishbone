#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dummy.py
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

from wishbone.protocol import Decode


class Dummy(Decode):

    '''**A dummy decoder.**

    A dummy decoder which yields unmodified data back.


    Parameters:

        n/a
    '''

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.handle_buffer_size = True

    def handleBytes(self, data):
        yield data

    handleString = handleBytes
    handleInt = handleBytes
    handleFloat = handleBytes
    handleDict = handleBytes
    handleList = handleBytes
    handleGenerator = handleBytes
    handleReadLinesMethod = handleBytes

    def flush(self):
        return
        yield
