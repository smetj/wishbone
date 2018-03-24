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


import os
from wishbone.protocol.decode.plain import Plain
import itertools
from wishbone.error import ProtocolError


def test_protocol_decode_plain_basic_string():

    p = Plain()
    for chunk in ["a\nb\nc\n", None]:
        for payload in p.handler(chunk):
            assert payload == "a\nb\nc\n"


def test_protocol_decode_plain_basic_binary():

    p = Plain()
    for chunk in [b"a\nb\nc\n\xc3\xa9", None]:
        for payload in p.handler(chunk):
            assert payload == "a\nb\nc\né"


def test_protocol_decode_plain_delimiter_string():

    a = itertools.cycle(["a", "b", "c"])

    p = Plain(delimiter="\n")
    for chunk in ["a\nb\nc\n", None]:
        for payload in p.handler(chunk):
            assert payload == next(a)


def test_protocol_decode_plain_delimiter_binary():

    a = itertools.cycle(["a", "b", "c", "é"])

    p = Plain(delimiter="\n")
    for chunk in [b"a\nb\nc\n\xc3\xa9", None]:
        for payload in p.handler(chunk):
            assert payload == next(a)


def test_protocol_decode_plain_readlines():

    result = itertools.cycle(["one", "two", "three", "four", "five"])

    try:
        os.unlink("./protocol_decode_test")
    except Exception as err:
        del(err)
    with open("./protocol_decode_test", "w") as w:
        w.write("one\ttwo\tthree\n")
        w.write("four\tfive")

    with open("./protocol_decode_test", "r") as r:
        p = Plain(delimiter="\t", strip_newline=True)
        for payload in p.handler(r):
            check = next(result)
            assert payload == check
    try:
        os.unlink("./protocol_decode_test")
    except Exception as err:
        del(err)


def test_protocol_decode_plain_basic_overflow():

    p = Plain(buffer_size=4)
    try:
        for chunk in ["a", "b", "c", "d", "e", None]:
            for payload in p.handler(chunk):
                payload
    except ProtocolError:
        assert True
    else:
        assert False
