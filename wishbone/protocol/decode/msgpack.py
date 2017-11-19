#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  msgpack.py
#
#  Copyright 2017 Jelle Smet <development@smetj.net>
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
from io import BytesIO
from msgpack import Unpacker
from msgpack.exceptions import BufferFull


class EndOfStream(Exception):
    pass


class MSGPack(Decode):

    '''**Decode MSGpack data into a Python data structure.**

    Convert a MSGPack bytestring into a Python data structure using the
    defined charset.

    Parameters:

        - charset(string)("utf-8")
           |  The charset to use to decode the bytestring data.

        - buffer_size(int)(4096)
           |  The max amount of bytes allowed to read for 1 event

    '''

    def __init__(self, charset="utf-8", buffer_size=4096):

        self.charset = charset
        self.buffer_size = buffer_size
        self.__leftover = ""
        self.buffer = BytesIO()
        self.__buffer_size = 0
        self.unpacker = Unpacker(encoding=self.charset, max_buffer_size=buffer_size)

    def handleBytes(self, data):

        try:
            self.unpacker.feed(data)
            for value in self.unpacker:
                if value:
                    yield value
                else:
                    return []
        except BufferFull:
            raise Exception("Buffer of %s bytes full." % (self.buffer_size))

    def handleReadlinesMethod(self, data):

        for item in data.readlines():
            for result in self.handler(item):
                yield result
