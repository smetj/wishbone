#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_queuepool.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from wishbone.queue import QueuePool
from wishbone.queue import MemoryQueue
from wishbone.error import QueuePoolError


def test_initialize():

    QueuePool()


def test_connect_bad():

    qp = QueuePool()
    try:
        qp.connect("one", "two")
    except QueuePoolError:
        assert False
    else:
        assert True


def test_connect_good():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())
    qp.registerQueue("two.inbox", MemoryQueue())

    try:
        qp.connect("one.outbox", "two.inbox")
    except Exception:
        assert False
    else:
        assert True


def test_connect_already_connected():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())
    qp.registerQueue("two.inbox", MemoryQueue())
    qp.registerQueue("two.outbox", MemoryQueue())
    qp.connect("one.outbox", "two.inbox")

    for expression in [
            ("one.outbox", "two.inbox"),
            ("two.inbox", "one.outbox"),
            ("two.inbox", "two.outbox"),
            ("one.outbox", "two.outbox")]:

        try:
            qp.connect(*expression)
        except QueuePoolError:
            assert True
        else:
            assert False


def test_getDirection():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())
    qp.registerQueue("two.inbox", MemoryQueue())
    qp.connect("one.outbox", "two.inbox")

    assert qp.getDirection("one.outbox") == "out"
    assert qp.getDirection("two.inbox") == "in"


def test_disconnect():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())
    qp.registerQueue("two.inbox", MemoryQueue())
    qp.connect("one.outbox", "two.inbox")
    qp.disconnect("two.inbox")

    assert len(qp.connections) == 0

    qp.connect("one.outbox", "two.inbox")
    qp.disconnect("one.outbox")

    assert len(qp.connections) == 0


def test_getConnection():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())
    qp.registerQueue("two.inbox", MemoryQueue())
    qp.connect("one.outbox", "two.inbox")

    assert qp.getConnection("one.outbox") == qp.getConnection("two.inbox")


def test_getConnectedQueue():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())
    qp.registerQueue("two.inbox", MemoryQueue())
    qp.connect("one.outbox", "two.inbox")

    assert qp.getConnectedQueue("one.outbox") == "two.inbox"
    assert qp.getConnectedQueue("two.inbox") == "one.outbox"


def test_getQueue():

    qp = QueuePool()
    q = MemoryQueue()
    qp.registerQueue("one.outbox", q)

    assert qp.getQueue("one.outbox") == q


def test_hasQueue():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())

    assert qp.hasQueue("one.outbox")
    assert not qp.hasQueue("blah")


def test_isConnected():

    qp = QueuePool()
    qp.registerQueue("one.outbox", MemoryQueue())
    qp.registerQueue("two.inbox", MemoryQueue())
    qp.connect("one.outbox", "two.inbox")

    assert qp.isConnected("one.outbox")
    assert qp.isConnected("two.inbox")

    qp.disconnect("one.outbox")
    assert not qp.isConnected("two.inbox")


def test_listQueues():

    qp = QueuePool()
    one = MemoryQueue()
    two = MemoryQueue()
    qp.registerQueue("one.outbox", one)
    qp.registerQueue("two.inbox", two)

    assert ("one.outbox", one) in list(qp.listQueues())
    assert ("two.inbox", two) in list(qp.listQueues())
