#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_match.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
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

from wishbone.event import Event
from wishbone.module import Match
from wishbone.actor import ActorConfig
from wishbone.error import QueueEmpty

from utils import getter


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
                { "smaller": "<:100" }
            ],
            "queue": [
                {"smaller":{}}
            ]
        },
        "smaller_equal": {
            "condition": [
                { "smaller_equal": "<=:100" }
            ],
            "queue": [
                {"smaller_equal":{}}
            ]
        },
        "equal": {
            "condition": [
                { "equal": "=:100" }
            ],
            "queue": [
                {"equal":{}}
            ]
        },
        "list_membership": {
            "condition": [
                { "list_membership": "in:test" }
            ],
            "queue": [
                {"list_membership":{}}
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
    assert int(getter(match.pool.queue.bigger_equal).data["bigger_equal"]) == 100
    assert int(getter(match.pool.queue.bigger_equal).data["bigger_equal"]) > 100

    #smaller
    one = Event("test")
    one.setData({"smaller": "99"})
    match.pool.queue.inbox.put(one)
    match.pool.queue.inbox.put(two)
    assert int(getter(match.pool.queue.smaller).data["smaller"]) < 100

    #smaller_equal
    one = Event("test")
    one.setData({"smaller_equal": "100"})
    two = Event("test")
    two.setData({"smaller_equal": "99"})
    match.pool.queue.inbox.put(one)
    match.pool.queue.inbox.put(two)
    assert int(getter(match.pool.queue.smaller_equal).data["smaller_equal"]) == 100
    assert int(getter(match.pool.queue.smaller_equal).data["smaller_equal"]) < 100

    #equal
    one = Event("test")
    one.setData({"equal": "100"})
    match.pool.queue.inbox.put(one)
    assert int(getter(match.pool.queue.equal).data["equal"]) == 100

    #list_membership
    one = Event("test")
    one.setData({"list_membership": ["one", "test", "two"]})
    match.pool.queue.inbox.put(one)
    assert "one" in getter(match.pool.queue.list_membership).data["list_membership"]

    match.stop()