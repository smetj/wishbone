#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_functions_template.py
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
import time
import os
import re


def test_wishbone_function_template_choice():

    lst = ["one", "two", "three"]
    f = ComponentManager().getComponentByName("wishbone.function.template.choice")(lst)
    assert f.get() in lst


def test_wishbone_function_template_cycle():

    lst = ["one", "two", "three"]
    f = ComponentManager().getComponentByName("wishbone.function.template.cycle")(lst)
    assert f.get() == "one"
    assert f.get() == "two"
    assert f.get() == "three"
    assert f.get() == "one"


def test_wishbone_function_template_epoch():

    f = ComponentManager().getComponentByName("wishbone.function.template.epoch")()
    assert type(f.get()) == float
    epoch = f.get()
    assert epoch > 0 and epoch < time.time()


def test_wishbone_function_template_pid():

    f = ComponentManager().getComponentByName("wishbone.function.template.pid")()
    assert f.get() == os.getpid()


def test_wishbone_function_template_random_bool():

    f = ComponentManager().getComponentByName("wishbone.function.template.random_bool")()
    assert f.get() in [True, False]


def test_wishbone_function_template_random_integer():

    f = ComponentManager().getComponentByName("wishbone.function.template.random_integer")(10, 15)
    value = f.get()
    assert value >= 10 and value <= 15


def test_wishbone_function_template_random_uuid():

    f = ComponentManager().getComponentByName("wishbone.function.template.random_uuid")()
    value = f.get()
    assert re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I).match(value) is not None


def test_wishbone_function_template_random_word():

    f = ComponentManager().getComponentByName("wishbone.function.template.random_word")()
    value = f.get()
    assert re.compile('\w*').match(value) is not None


def test_wishbone_function_template_strftime():

    f = ComponentManager().getComponentByName("wishbone.function.template.strftime")()
    assert f.get(0, 'YYYY-MM-DD HH:mm:ss ZZ') == '1970-01-01 00:00:00 +00:00'


def test_wishbone_function_template_regexTrue():

    f = ComponentManager().getComponentByName("wishbone.function.template.regex")()
    assert f.get('.*', "hello")


def test_wishbone_function_template_regexFalse():

    f = ComponentManager().getComponentByName("wishbone.function.template.regex")()
    assert not f.get('.*$.', "hello")


def test_wishbone_function_template_version():

    f = ComponentManager().getComponentByName("wishbone.function.template.version")()
    assert f.get() == '3.0.1'


def test_wishbone_function_template_environment():

    f = ComponentManager().getComponentByName("wishbone.function.template.environment")()
    assert '/' in f.get("PATH")
