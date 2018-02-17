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


from wishbone.error import ProtocolError
from wishbone.protocol import Decode
from json import loads
from io import StringIO


class JSON(Decode):

    def __init__(self, charset='utf-8', delimiter=None, buffer_size=4096):

        self.charset = charset
        if isinstance(delimiter, bytes):
            self.delimiter = delimiter.decode(charset, 'strict')
        else:
            self.delimiter = delimiter
        self.buffer_size = buffer_size
        self.buffer = StringIO()

    def handleBytes(self, data):

        for item in self.handler(data.decode(self.charset, "strict")):
            yield self.handler(item)

    def handleDict(self, data):

        return data

    def handleGenerator(self, data):

        for chunk in data:
            for item in self.handler(chunk):
                yield item

    def handleReadLinesMethod(self, data):

        for chunk in data.readlines():
            for item in self.handler(chunk):
                yield item

    def handleString(self, data):

        self.buffer.write(data)
        self.buffer.seek(0)

        if self.delimiter is not None and self.delimiter in self.buffer.getvalue():
            for item in self.buffer.getvalue().split(self.delimiter):
                if item == "":
                    next
                else:
                    try:
                        yield loads(item)
                    except Exception as err:
                        raise ProtocolError(err)
            self.buffer.truncate(0)
        else:
            self.buffer.seek(0, 2)

    def flush(self):

        if len(self.buffer.getvalue()) == 0:
            return
            yield
        else:
            try:
                yield loads(
                    self.buffer.getvalue()
                )
            except Exception as err:
                raise ProtocolError(err)
            else:
                self.buffer.seek(0)
                self.buffer.truncate()
