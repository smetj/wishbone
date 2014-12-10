#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_wishbone.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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

import pytest
import warnings
warnings.simplefilter('error', DeprecationWarning)

from gevent import spawn
from wishbone import QueuePool
from wishbone import Queue

from wishbone.event import Event

from wishbone.module import TestEvent
from wishbone.module import Fanout
from wishbone.module import Funnel
from wishbone.module import Match

from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty
from wishbone.event import Event

from gevent import sleep

def test_listQueues():
    q = QueuePool(1)
    q.createQueue("hello")
    assert list(q.listQueues(names=True)) == ['hello', 'failed', 'success', 'logs', 'metrics']


def test_createQueue():
    q = QueuePool(1)
    q.createQueue("test")
    assert (q.queue.test)


def test_hasQueue():
    q = QueuePool(1)
    q.createQueue("test")
    assert (q.hasQueue("test"))


def test_getQueue():
    q = QueuePool(1)
    q.createQueue("test")
    assert isinstance(q.getQueue("test"), Queue)


def test_module_fanout():

    actor_config = ActorConfig('fanout', 100, 1)
    fanout = Fanout(actor_config, deep_copy=True)
    fanout.pool.queue.inbox.disableFallThrough()

    fanout.pool.createQueue("one")
    fanout.pool.queue.one.disableFallThrough()

    fanout.pool.createQueue("two")
    fanout.pool.queue.two.disableFallThrough()

    fanout.start()

    e = Event('test')
    e.setData("hello")

    fanout.pool.queue.inbox.put(e)
    one=getter(fanout.pool.queue.one)
    two=getter(fanout.pool.queue.two)

    fanout.stop()

    assert one.raw()["test"]["data"] == "hello"
    assert two.raw()["test"]["data"] == "hello"
    assert id(one) != id(two)


def test_module_funnel():

    actor_config = ActorConfig('funnel', 100, 1)
    funnel = Funnel(actor_config)
    funnel.pool.queue.outbox.disableFallThrough()

    funnel.pool.createQueue("one")
    funnel.pool.queue.one.disableFallThrough()

    funnel.pool.createQueue("two")
    funnel.pool.queue.two.disableFallThrough()

    funnel.start()

    event_one = Event("test")
    event_one.setData("one")

    event_two = Event("test")
    event_two.setData("two")

    funnel.pool.queue.one.put(event_one)
    funnel.pool.queue.two.put(event_two)

    assert getter(funnel.pool.queue.outbox).raw()["test"]["data"] == "one"
    assert getter(funnel.pool.queue.outbox).raw()["test"]["data"] == "two"

    funnel.stop()


def test_module_match():

    rules = {
        "regex": {
            "condition": [
                { "regex": "re:.*?two.*" }
            ],
            "queue": [
                {"regex":{}}
            ]
        },
        "neg_regex": {
            "condition": [
                { "neg_regex": "!re:.*?two.*" }
            ],
            "queue": [
                {"neg_regex":{}}
            ]
        },
        "bigger": {
            "condition": [
                { "bigger": ">:10" }
            ],
            "queue": [
                {"bigger":{}}
            ]
        },
        "bigger_equal": {
            "condition": [
                { "bigger_equal": ">=:10" }
            ],
            "queue": [
                {"bigger_equal":{}}
            ]
        },
        "smaller": {
            "condition": [
                { "smaller": "<:10" }
            ],
            "queue": [
                {"smaller":{}}
            ]
        },
        "smaller_equal": {
            "condition": [
                { "smaller_equal": "<=:10" }
            ],
            "queue": [
                {"smaller_equal":{}}
            ]
        },
        "equal": {
            "condition": [
                { "equal": "=:10" }
            ],
            "queue": [
                {"equal":{}}
            ]
        },
        "in": {
            "condition": [
                { "in": "in:test" }
            ],
            "queue": [
                {"in":{}}
            ]
        }
    }

    actor_config = ActorConfig('match', 100, 1)
    match = Match(actor_config, rules=rules)

    match.pool.queue.inbox.disableFallThrough()
    for queue in rules.keys():
        match.pool.createQueue(queue)
        getattr(match.pool.queue, queue).disableFallThrough()

    match.start()

    #regex
    e = Event("test")
    e.setData({"regex": "one two three"})
    match.pool.queue.inbox.put(e)
    assert getter(match.pool.queue.regex).data["regex"] == "one two three"

    #neg_regex
    e = Event("test")
    e.setData({"neg_regex": "one twwo three"})
    match.pool.queue.inbox.put(e)
    assert getter(match.pool.queue.neg_regex).data["neg_regex"] == "one twwo three"

    #bigger
    e = Event("test")
    e.setData({"bigger": "100"})
    match.pool.queue.inbox.put(e)
    assert getter(match.pool.queue.bigger).data["bigger"] == "100"

    #bigger_equal
    one = Event("test")
    one.setData({"bigger_equal": "100"})
    two = Event("test")
    two.setData({"bigger_equal": "101"})
    match.pool.queue.inbox.put(one)
    match.pool.queue.inbox.put(two)
    assert getter(match.pool.queue.bigger_equal).data["bigger_equal"] == "100"
    assert getter(match.pool.queue.bigger_equal).data["bigger_equal"] > "100"

    match.stop()


def getter(queue):
    counter = 0
    while True:
        counter += 1
        if counter >= 5:
            return None
        else:
            try:
                return queue.get()
            except QueueEmpty as err:
                err.waitUntilContent()
