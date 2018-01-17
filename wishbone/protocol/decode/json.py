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


from wishbone.protocol import Decode
from wishbone.error import ProtocolError
from io import BytesIO
from json import loads


class EndOfStream(Exception):
    pass


class JSON(Decode):

    '''**Decode JSON data into a Python data structure.**

    Convert a JSON bytestring into a Python data structure using the defined
    charset.

    Parameters:

        - charset(string)("utf-8")
           |  The charset to use to decode the bytestring data.

        - delimiter(string)("\\n")
           |  The delimiter between multiple events

        - buffer_size(int)(4096)
           |  The max amount of bytes allowed to read for 1 event
    '''

    def __init__(self, charset="utf-8", delimiter=None, buffer_size=4096):

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
            return []
        else:
            data = self.__leftover + data.decode(self.charset)
            if len(data) > self.buffer_size:
                self.reset()
                raise ProtocolError("Buffer exceeded")
            while self.delimiter in data:
                item, data = data.split(self.delimiter, 1)
                if item != "":
                    try:
                        self.reset()
                        yield loads(item)
                    except Exception as err:
                        raise ProtocolError("ProtcolError: %s" % (err))
            self.__leftover = data

    def __plainNoDelimiter(self, data):

        if data is None or data == b'':
            self.buffer.seek(0)
            try:
                yield loads(self.buffer.getvalue().decode(self.charset))
                self.reset()
            except Exception as err:
                self.reset()
                raise ProtocolError("ProtcolError: %s" % (err))
        else:
            self.__buffer_size += self.buffer.write(data)
            if self.__buffer_size > self.buffer_size:
                self.reset()
                raise ProtocolError("Buffer exceeded.")
            return []

    def handleString(self, data):
        if len(data) == 0:
            raise StopIteration
        else:
            try:
                yield loads(data)
            except Exception as err:
                self.reset()
                raise ProtocolError("ProtocolError: %s" % (err))

    def handleReadlinesMethod(self, data):

        for item in data.readlines() + [""]:
            for result in self.handler(item):
                yield result
        self.reset()

    def reset(self):

        self.__buffer_size = 0
        self.buffer = BytesIO()
