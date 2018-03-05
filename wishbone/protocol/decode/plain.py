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
from io import StringIO


class Plain(Decode):

    def __init__(self, charset='utf-8', delimiter=None, buffer_size=4096, strip_newline=False):

        self.charset = charset
        if isinstance(delimiter, bytes):
            self.delimiter = delimiter.decode(charset, 'strict')
        else:
            self.delimiter = delimiter
        self.buffer_size = buffer_size
        self.strip_newline = strip_newline
        self.buffer = StringIO()

    def handleBytes(self, data):

        for chunk in self.handler(data.decode(self.charset, "strict")):
            yield chunk

    def handleDict(self, data):

        return data

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
                    if self.strip_newline:
                        yield item.rstrip()
                    else:
                        yield item
            self.buffer.truncate(0)
        else:
            self.buffer.seek(0, 2)

    def flush(self):

        if len(self.buffer.getvalue()) == 0:
            return
            yield
        else:
            if self.strip_newline:
                yield self.buffer.getvalue().rstrip()
            else:
                yield self.buffer.getvalue()
            self.buffer.seek(0)
            self.buffer.truncate(0)
