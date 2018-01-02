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


class Cleanup(object):

    def __init__(self, path):

        self.path = path

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args):

        try:
            unlink(self.path)
        except Exception:
            pass


def test_yaml_default():

    with Cleanup("/tmp/test.yaml"):
        s = StructuredDataFile(expect_json=False, expect_kv=False)

        with open("/tmp/test.yaml", "w") as f:
            f.write("one: 1\n")

        assert s.get("/tmp/test.yaml") == {"one": 1}


def test_json_default():

    with Cleanup("/tmp/test.json"):
        s = StructuredDataFile(expect_yaml=False, expect_kv=False)

        with open("/tmp/test.json", "w") as f:
            f.write('{"one": 1}\n')

        assert s.get("/tmp/test.json") == {"one": 1}


def test_kv_default():

    with Cleanup("/tmp/test.kv"):
        s = StructuredDataFile(expect_yaml=False, expect_json=False)

        with open("/tmp/test.kv", "w") as f:
            f.write("one: 1\n")

        assert s.get("/tmp/test.kv") == {"one": "1"}



