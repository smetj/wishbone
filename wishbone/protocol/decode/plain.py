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
from io import BytesIO, StringIO


class EndOfStream(Exception):
    pass


class BytesBuffer(object):

    leftover = ""
    buffer = BytesIO()
    size = 0


class StringBuffer(object):

    leftover = ""
    buffer = StringIO()
    size = 0


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

        self.bytes_buffer = BytesBuffer()
        self.string_buffer = StringBuffer()

        if delimiter is None:
            self.handleBytes = self.__plainNoDelimiterBytes
            self.handleString = self.__plainNoDelimiterString
        else:
            self.handleBytes = self.__plainDelimiterBytes
            self.handleString = self.__plainDelimiterString

    def __plainDelimiterBytes(self, data):

        if len(data) == 0:
            yield self.bytes_buffer.leftover.rstrip()
            self.bytes_buffer.leftover = ""
        else:
            data = self.bytes_buffer.leftover + data.decode(self.charset)
            if len(data) > self.buffer_size:
                raise Exception("Buffer exceeded")
            while self.delimiter in data:
                item, data = data.split(self.delimiter, 1)
                yield item
            self.bytes_buffer.leftover = data

    def __plainNoDelimiterBytes(self, data):

        if len(data) == 0:
            self.bytes_buffer.buffer.seek(0)
            yield self.bytes_buffer.buffer.getvalue().decode(self.charset).rstrip(self.delimiter)
        else:
            self.bytes_buffer.size += self.bytes_buffer.buffer.write(data)
            if self.bytes_buffer.size > self.buffer_size:
                raise Exception("Buffer exceeded.")
            return []

    def __plainDelimiterString(self, data):

        if len(data) == 0:
            if self.string_buffer.leftover.rstrip() == "":
                raise StopIteration
            else:
                yield self.string_buffer.leftover.rstrip()
                self.string_buffer.leftover = ""

        else:
            data = self.string_buffer.leftover + data
            if len(data) > self.buffer_size:
                raise Exception("Buffer exceeded")
            while self.delimiter in data:
                item, data = data.split(self.delimiter, 1)
                yield item
            self.string_buffer.leftover = data

    def __plainNoDelimiterString(self, data):

        if len(data) == 0:
            self.string_buffer.buffer.seek(0)
            yield self.string_buffer.buffer.getvalue().rstrip(self.delimiter)
        else:
            self.string_buffer.size += self.string_buffer.buffer.write(data)
            if self.string_buffer.size > self.buffer_size:
                raise Exception("Buffer exceeded.")
            return []

    def handleReadlinesMethod(self, data):

        for item in data.readlines() + [""]:
            for result in self.handler(item):
                if result != "":
                    yield result
