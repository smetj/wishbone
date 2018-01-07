#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plain.py
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

from wishbone.protocol import Decode
from io import BytesIO


class EndOfStream(Exception):
    pass


class Plain(Decode):

    '''**Decode plaintext using the defined charset.**

    Converts text bytestring into unicode using the defined charset.

    Parameters:

        - charset(string)("utf-8")
           |  The charset to use to decode the bytestring data.

        - delimiter(string)("\\n")
           |  The delimiter between multiple events

        - buffer_size(int)(4096)
           |  The max amount of bytes allowed to read for 1 event
    '''

    def __init__(self, charset="utf-8", delimiter="\n", buffer_size=4096):

        self.charset = charset
        self.delimiter = delimiter
        self.buffer_size = buffer_size
        self.__leftover = ""
        self.buffer = BytesIO()
        self.__buffer_size = 0

        if delimiter is None:
            self.handleBytes = self.__plainNoDelimiter
        else:
            self.handleBytes = self.__plainDelimiter

    def __plainDelimiter(self, data):

        if data is None or data == b'':
            yield self.__leftover.rstrip()
            self.__leftover = ""
        else:
            data = self.__leftover + data.decode(self.charset)
            if len(data) > self.buffer_size:
                raise Exception("Buffer exceeded")
            while self.delimiter in data:
                item, data = data.split(self.delimiter, 1)
                yield item
            self.__leftover = data

    def __plainNoDelimiter(self, data):

        if data is None or data == b'':
            self.buffer.seek(0)
            yield self.buffer.getvalue().decode(self.charset).rstrip(self.delimiter)
        else:
            self.__buffer_size += self.buffer.write(data)
            if self.__buffer_size > self.buffer_size:
                raise Exception("Buffer exceeded.")
            return []

    def handleReadlinesMethod(self, data):

        for item in data.readlines() + [None]:
            for result in self.handler(item):
                if result != "":
                    yield result
