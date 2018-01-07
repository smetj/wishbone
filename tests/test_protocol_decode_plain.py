#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_protocol_decode_plain.py
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


from wishbone.protocol.decode.plain import Plain
import itertools


def test_protocol_decode_plain_basic():

    a = itertools.cycle(["a", "b", "c"])
    p = Plain()
    for payload in p.handler(b"a\nb\nc\n"):
        assert payload == next(a)
