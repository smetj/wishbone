#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_modify.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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

from wishbone.event import Event
from wishbone.module.modify import Modify
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter


def get_actor(expression):
    actor_config = ActorConfig('modify', 100, 1, {}, "")
    modify = Modify(actor_config, expressions=[expression])

    modify.pool.queue.inbox.disableFallThrough()
    modify.pool.queue.outbox.disableFallThrough()
    modify.start()

    return modify


def test_module_add_item():

    a = get_actor({"add_item": ["fubar", "@data"]})
    e = Event(["one", "two", "three"])
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert "fubar" in one.get('@data')


def test_module_copy():

    a = get_actor({"copy": ["@data", "@tmp.copy", "n/a"]})
    e = Event({"greeting": "hi"})
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert "hi" == one.get('@tmp.copy')["greeting"]
    assert id(one.get("@data")) != id(one.get("@tmp.copy"))

def test_module_copy_default():

    a = get_actor({"copy": ["does.not.exist", "@tmp.copy", "default"]})
    e = Event({"greeting": "hi"})
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert "default" == one.get('@tmp.copy')

def test_module_del_item():

    a = get_actor({"del_item": ["fubar", "@data"]})
    e = Event(["one", "two", "three", "fubar"])
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert "fubar" not in one.get('@data')


def test_module_delete():

    a = get_actor({"delete": ["@data.two"]})
    e = Event({"one": 1, "two": 2})
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert "two" not in one.get('@data').keys()


def test_module_extract():

    a = get_actor({"extract": ["destination", "(?P<one>.*?)\ (?P<two>.*)\ (?P<three>.*)", "@data"]})
    e = Event("een twee drie")
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get('destination.one') == "een"


def test_module_lowercase():

    a = get_actor({"lowercase": ["@data.lower"]})
    e = Event({"lower": "HELLO"})
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get('@data.lower') == "hello"


def test_module_modify_set():

    a = get_actor({"set": ["hi", "blah"]})
    e = Event('hello')
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get('blah') == "hi"


def test_module_uppercase():

    a = get_actor({"uppercase": ["@data.upper"]})
    e = Event({"upper": "hello"})
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get('@data.upper') == "HELLO"


def test_module_template():

    a = get_actor({"template": ["result", "Good day in {language} is {word}.", "@data"]})
    e = Event({"language": "German", "word": "gutten Tag"})
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get('result') == "Good day in German is gutten Tag."


def test_module_time():

    a = get_actor({"time": ["epoch", "X"]})
    e = Event("hello")
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)

def test_module_replace():

    a = get_actor({"replace": ['\d', "X", "@data"]})
    e = Event("hello 123 hello")
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get('@data') == "hello XXX hello"

def test_module_join():

    a = get_actor({"join": ['@data', ",", "@tmp.joined"]})
    e = Event(["one", "two", "three"])
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get('@tmp.joined') == "one,two,three"

def test_module_merge():

    a = get_actor({"merge": ['@tmp.one', '@tmp.two', '@data']})
    e = Event()
    e.set(["one"], "@tmp.one")
    e.set(["two"], "@tmp.two")
    a.pool.queue.inbox.put(e)
    one = getter(a.pool.queue.outbox)
    assert one.get() == ["one", "two"]
