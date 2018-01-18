#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_protocol_decode_msgpack.py
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


from wishbone.protocol.decode.msgpack import MSGPack
from wishbone.error import ProtocolError


class ReadlineMock():

    data = [
        b'\x93\x01',
        b'\x02\x03'
    ]

    def readlines(self):

        return self.data


def test_protocol_decode_msgpack_basic():

    m = MSGPack()
    for item in m.handler(b'\x93\x01\x02\x03'):
        assert item == [1, 2, 3]


def test_protocol_decode_msgpack_basic_chunk():

    m = MSGPack()
    for chunk in [b'\x93\x01\x02\x03', None]:
        for item in m.handler(chunk):
            assert item == [1, 2, 3]


def test_protocol_decode_msgpack_basic_chunk_size():

    try:
        m = MSGPack(buffer_size=2)
        for chunk in [b'\x93\x01\x02\x03', None]:
            for item in m.handler(chunk):
                assert item == [1, 2, 3]
    except ProtocolError:
        assert True
    else:
        assert False


def test_protocol_decode_msgpack_unicode():

    m = MSGPack()
    for item in m.handler(b'\x91\xa2\xce\xb1'):
        assert item == ["α"]


def test_protocol_decode_msgpack_readlines():

    m = MSGPack()
    reader = ReadlineMock()
    for item in m.handler(reader):
        assert item == [1, 2, 3]
