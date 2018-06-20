#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_functions.py
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

from wishbone.componentmanager import ComponentManager
from wishbone.event import Event


def test_wishbone_function_module_append():

    e = Event({"tags": ["one", "two"]})
    f = ComponentManager().getComponentByName("wishbone.function.module.append")(
        "three", "data.tags"
    )
    assert f.do(e).get() == {"tags": ["one", "two", "three"]}


def test_wishbone_function_module_uppercase():

    e = Event({"case": "upper"})
    f = ComponentManager().getComponentByName("wishbone.function.module.uppercase")(
        "data.case", "data.case"
    )
    assert f.do(e).get() == {"case": "UPPER"}


def test_wishbone_function_module_lowercase():

    e = Event({"case": "LOWER"})
    f = ComponentManager().getComponentByName("wishbone.function.module.lowercase")(
        "data.case", "data.case"
    )
    assert f.do(e).get() == {"case": "lower"}


def test_wishbone_function_module_set():

    e = Event({"hey": "how"})
    f = ComponentManager().getComponentByName("wishbone.function.module.set")(
        {"greeting": "hello"}, "tmp.test"
    )
    assert f.do(e).get("tmp.test") == {"greeting": "hello"}
