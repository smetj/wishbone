#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_wishbone.py
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

from wishbone.event import Event
from wishbone.error import TTLExpired, InvalidData, BulkFull


def test_event_bulk_default():

    e = Event(bulk=True)
    assert e.dump()["bulk"]


def test_event_appendBulk():

    e = Event(bulk=True)
    ee = Event({"one": 1})

    e.appendBulk(ee)
    assert e.dump()["data"][0]["uuid"] == ee.data["uuid"]


def test_event_appendBulkFull():

    e = Event(bulk=True, bulk_size=1)
    ee = Event({"one": 1})

    e.appendBulk(ee)
    try:
        e.appendBulk(ee)
    except BulkFull:
        assert True
    else:
        assert False


def test_event_appendBulkBad():

    normal_event = Event()

    try:
        normal_event.appendBulk(Event())
    except Exception:
        assert True
    else:
        assert False

    bulk_event = Event(bulk=True)
    try:
        bulk_event.appendBulk("hello")
    except Exception:
        assert True
    else:
        assert False


def test_event_isBulk():

    a = Event(bulk=True)
    assert a.isBulk()


def test_event_clone():

    a = Event({"one": 1, "two": 2})
    b = a.clone()

    assert id(a.data) != id(b.data)
    assert not a.data["cloned"]
    assert b.data["cloned"]
    assert b.data["uuid_previous"][0] == a.data["uuid"]


def test_event_copy():

    a = Event({"one": 1, "two": 2})
    a.copy("data.one", "data.two")
    assert a.dump()["data"]["two"] == 1


def test_event_decrementTTL():

    a = Event(ttl=2)
    a.decrementTTL()
    assert a.dump()["ttl"] == 1

    try:
        a.decrementTTL()
    except TTLExpired:
        assert True
    else:
        assert False


def test_event_delete():

    a = Event({"one": 1, "two": 2})
    a.delete("data.two")

    try:
        a.get("data.two")
    except KeyError:
        assert True
    else:
        assert False


def test_event_dump():

    from wishbone.event import EVENT_RESERVED

    data = {"one": 1, "two": 2}
    a = Event(data)
    result = a.dump()

    for key in EVENT_RESERVED:
        assert key in result

    assert result["data"] == data
    assert isinstance(result["timestamp"], float)


def test_event_render():

    e = Event({"one": 1, "two": 2})
    assert e.render("{{data.one}} is a number and so is {{data.two}}") == "1 is a number and so is 2"


def test_event_render_error():

    e = Event({"one": 1, "two": 2})

    try:
        e.render("{{data.one} is a number and so is {{data.two}}")
    except InvalidData:
        assert True
    else:
        assert False


def test_event_get():

    e = Event({"one": 1, "two": {"three": 3}})
    assert e.get("data.two.three") == 3


def test_event_has():

    e = Event({"one": 1, "two": {"three": 3}})
    assert e.has("data.one")
    assert not e.has("blah")


def test_event_set():

    e = Event({"one": 1, "two": {"three": 3}})
    e.set({"four": 4}, "data.two.three")
    assert e.dump()["data"]["two"]["three"]["four"] == 4


def test_event_slurp():

    a = Event()
    b = Event()
    b.slurp(a.dump())

    assert a.get('uuid') == b.get('uuid')


def test_event_slurp_bad():

    a = Event()
    del(a.data["uuid"])
    b = Event()

    try:
        b.slurp(a.dump())
    except InvalidData:
        assert True
    else:
        assert False


def test_event_get_error():

    e = Event({"one": 1, "two": {"three": 3}})
    try:
        e.get("data.blah")
    except KeyError:
        assert True
    else:
        assert False


def test_event_uuid():

    e = Event()
    assert e.get('uuid')


def test_extractBulkItems():

    from wishbone.event import extractBulkItems

    e = Event(bulk=True)
    e.appendBulk(Event({"one": 1}))
    e.appendBulk(Event({"two": 2}))
    e.appendBulk(Event({"three": 3}))

    for item in extractBulkItems(e):
        assert isinstance(item, Event)


def test_extractBulkItemValues():

    from wishbone.event import extractBulkItemValues

    e = Event(bulk=True)
    e.appendBulk(Event({"one": 1}))
    e.appendBulk(Event({"two": 2}))
    e.appendBulk(Event({"three": 3}))

    for item in extractBulkItemValues(e, "data"):
        assert item in [{"one": 1}, {"two": 2}, {"three": 3}]


def test_merge_dict():

    e = Event({"one": 1})
    e.merge({"two": 2})

    assert e.dump()["data"] == {"one": 1, "two": 2}


def test_merge_list():

    e = Event(["one"])
    e.merge(["two"])

    assert e.dump()["data"] == ["one", "two"]


def test_merge_fail():

    e = Event("hi")

    try:
        e.merge(["two"])
    except InvalidData:
        assert True
    else:
        assert False
