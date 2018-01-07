#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_componentmanager.py
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

c = ComponentManager()


def test_exists():

    assert c.exists('wishbone.module.input.inotify') is True


def test_getComponent():

    from wishbone.module import wb_inotify
    assert c.getComponent('wishbone', 'module', 'input', 'inotify') == wb_inotify.WBInotify


def test_getComponentByName():

    from wishbone.module import wb_inotify
    assert c.getComponentByName('wishbone.module.input.inotify') == wb_inotify.WBInotify


def test_getComponentList():

    assert c.getComponentList()
    for item in c.getComponentList():
        assert isinstance(item, tuple)
        assert len(item) == 4
        break


def test_getComponentDoc():

    assert "Parameters" in c.getComponentDoc('wishbone', 'module', 'input', 'inotify')


def test_getComponentTitle():

    assert "inotify" in c.getComponentTitle('wishbone', 'module', 'input', 'inotify')


def test_getComponentVersion():

    import pkg_resources
    assert pkg_resources.get_distribution("wishbone").version == c.getComponentVersion('wishbone', 'module', 'input', 'inotify')


def test_validateComponentName():

    assert c.validateComponentName('wishbone.module.flow.tippingbucket') is True
    try:
        c.validateComponentName('wishbone.flow.tippingbucket')
    except Exception:
        assert True
    else:
        assert False


def test_getComponentTable():

    assert c.getComponentTable()[-1][0] == "+"
