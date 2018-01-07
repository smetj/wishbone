#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_protocol_decode_json.py
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


from wishbone.protocol.encode.msgpack import MSGPack


def test_protocol_encode_json_dict():

    m = MSGPack()
    assert m.handler({"one": 1}) == b'\x81\xa3one\x01'


def test_protocol_encode_json_list():

    m = MSGPack()
    assert m.handler(["one", "two"]) == b'\x92\xa3one\xa3two'
