#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

from wishbone.error import ProtocolError


class Decode(object):

    def handler(self, data):

        if isinstance(data, bytes) or data is None:
            return self.handleBytes(data)
        elif isinstance(data, str) or data is None:
            return self.handleString(data)
        elif isinstance(data, int) or data is None:
            return self.handleInt(data)
        elif isinstance(data, float) or data is None:
            return self.handleFloat(data)
        elif isinstance(data, dict) or data is None:
            return self.handleDict(data)
        elif isinstance(data, list) or data is None:
            return self.handleList(data)
        elif hasattr(data, "readlines") and callable(data.readlines):
            return self.handleReadlinesMethod(data)
        else:
            raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleBytes(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleString(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleInt(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleFloat(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleUnicode(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleDict(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleList(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleReadLinesMethod(self, data):
        raise ProtocolError("%s is not supported by this Decoder." % (type(data)))


class Encode(object):

    def handler(self, data):

        if isinstance(data, bytes) or data is None:
            return self.handleBytes(data)
        elif isinstance(data, str) or data is None:
            return self.handleString(data)
        elif isinstance(data, int) or data is None:
            return self.handleInt(data)
        elif isinstance(data, float) or data is None:
            return self.handleFloat(data)
        elif isinstance(data, dict) or data is None:
            return self.handleDict(data)
        elif isinstance(data, list) or data is None:
            return self.handleList(data)
        else:
            raise ProtocolError("%s is not supported by this Decoder." % (type(data)))

    def handleBytes(self, data):
        raise ProtocolError("%s is not supported by this Encoder." % (type(data)))

    def handleString(self, data):
        raise ProtocolError("%s is not supported by this Encoder." % (type(data)))

    def handleInt(self, data):
        raise ProtocolError("%s is not supported by this Encoder." % (type(data)))

    def handleFloat(self, data):
        raise ProtocolError("%s is not supported by this Encoder." % (type(data)))

    def handleUnicode(self, data):
        raise ProtocolError("%s is not supported by this Encoder." % (type(data)))

    def handleDict(self, data):
        raise ProtocolError("%s is not supported by this Encoder." % (type(data)))

    def handleList(self, data):
        raise ProtocolError("%s is not supported by this Encoder." % (type(data)))
