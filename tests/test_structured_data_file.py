#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_structured_data_file.py
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


from wishbone.utils import StructuredDataFile
from os import unlink


class TempFile(object):
    def __init__(self, filename, content):

        self.filename = filename
        with open(filename, "w") as f:
            f.write(content)

    def __enter__(self, *args, **kwargs):

        return self

    def __exit__(self, *args, **kwargs):

        unlink(self.filename)


def test_yaml_default():

    with TempFile("/tmp/test.yaml", "one: 1\n"):
        s = StructuredDataFile(expect_json=False, expect_kv=False)
        assert s.get("/tmp/test.yaml") == {"one": 1}


def test_json_default():

    with TempFile("/tmp/test.json", '{"one": 1}\n'):
        s = StructuredDataFile(expect_yaml=False, expect_kv=False)
        assert s.get("/tmp/test.json") == {"one": 1}


def test_kv_default():

    with TempFile("/tmp/test.kv", "one: 1\n"):
        s = StructuredDataFile(expect_yaml=False, expect_json=False)
        assert s.get("/tmp/test.kv") == {"one": "1"}


def test_dump_items():

    with TempFile("/tmp/one.json", '{"one": 1}'), TempFile(
        "/tmp/two.json", '{"two": 2}'
    ):
        s = StructuredDataFile()
        s.load("/tmp/one.json")
        s.load("/tmp/two.json")

        for item in s.dumpItems():
            assert "one" in item or "two" in item
