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

RULES = {
    "regex": {
        "condition": [
            {"regex": "re:.*?two.*"}
        ],
        "queue": [
            {"regex": {}}
        ]
    },
    "neg_regex": {
        "condition": [
            {"neg_regex": "!re:.*?two.*"}
        ],
        "queue": [
            {"neg_regex": {}}
        ]
    },
    "bigger": {
        "condition": [
            {"bigger": ">:10"}
        ],
        "queue": [
            {"bigger": {}}
        ]
    },
    "bigger_equal": {
        "condition": [
            {"bigger_equal": ">=:10"}
        ],
        "queue": [
            {"bigger_equal": {}}
        ]
    },
    "smaller": {
        "condition": [
            {"smaller": "<:100"}
        ],
        "queue": [
            {"smaller": {}}
        ]
    },
    "smaller_equal": {
        "condition": [
            {"smaller_equal": "<=:100"}
        ],
        "queue": [
            {"smaller_equal": {}}
        ]
    },
    "equal": {
        "condition": [
            {"equal": "=:100"}
        ],
        "queue": [
            {"equal": {}}
        ]
    },
    "list_membership": {
        "condition": [
            {"list_membership": "in:test"}
        ],
        "queue": [
            {"list_membership": {}}
        ]
    }
}

def generate_actor(rules):

    actor_config = ActorConfig('match', 100, 1, {})
    match = Match(actor_config, rules=rules)

    match.pool.queue.inbox.disableFallThrough()
    for queue in rules.keys():
        match.pool.createQueue(queue)
        getattr(match.pool.queue, queue).disableFallThrough()

    match.start()
    return match


def test_regex():

    rule = {"regex": {
        "condition": [
            {"regex": "re:.*?two.*"}
        ],
        "queue": [
            {"regex": {}}
        ]
    }}

    actor = generate_actor(rule)
    e = Event("test")
    e.setData({"regex": "one two three"})
    actor.pool.queue.inbox.put(e)
    assert getter(actor.pool.queue.regex).data["regex"] == "one two three"


def test_negative_regex():

    rule = {"neg_regex": {
        "condition": [
            {"neg_regex": "!re:.*?two.*"}
        ],
        "queue": [
            {"neg_regex": {}}
        ]
    }}

    actor = generate_actor(rule)
    e = Event("test")
    e.setData({"neg_regex": "one twwo three"})
    actor.pool.queue.inbox.put(e)
    assert getter(actor.pool.queue.neg_regex).data["neg_regex"] == "one twwo three"


def test_bigger_than():

    rule = {"bigger": {
        "condition": [
            {"bigger": ">:10"}
        ],
        "queue": [
            {"bigger": {}}
        ]
    }}

    actor = generate_actor(rule)
    e = Event("test")
    e.setData({"bigger": "100"})
    actor.pool.queue.inbox.put(e)
    assert getter(actor.pool.queue.bigger).data["bigger"] == "100"


def test_bigger_than_equal_to():

    rule = {"bigger_equal": {
        "condition": [
            {"bigger_equal": ">=:10"}
        ],
        "queue": [
            {"bigger_equal": {}}
        ]
    }}

    actor = generate_actor(rule)
    one = Event("test")
    one.setData({"bigger_equal": "100"})
    two = Event("test")
    two.setData({"bigger_equal": "101"})
    actor.pool.queue.inbox.put(one)
    actor.pool.queue.inbox.put(two)
    assert int(getter(actor.pool.queue.bigger_equal).data["bigger_equal"]) == 100
    assert int(getter(actor.pool.queue.bigger_equal).data["bigger_equal"]) > 100


def test_smaller_than():

    rule = {"smaller": {
        "condition": [
            {"smaller": "<:100"}
        ],
        "queue": [
            {"smaller": {}}
        ]
    }}

    actor = generate_actor(rule)
    one = Event("test")
    one.setData({"smaller": "99"})
    actor.pool.queue.inbox.put(one)
    assert int(getter(actor.pool.queue.smaller).data["smaller"]) < 100


def test_smaller_than_equal_to():

    rule = {"smaller_equal": {
        "condition": [
            {"smaller_equal": "<=:100"}
        ],
        "queue": [
            {"smaller_equal": {}}
        ]
    }}

    actor = generate_actor(rule)
    one = Event("test")
    one.setData({"smaller_equal": "100"})
    two = Event("test")
    two.setData({"smaller_equal": "99"})
    actor.pool.queue.inbox.put(one)
    actor.pool.queue.inbox.put(two)
    assert int(getter(actor.pool.queue.smaller_equal).data["smaller_equal"]) == 100
    assert int(getter(actor.pool.queue.smaller_equal).data["smaller_equal"]) < 100


def test_equal_to():

    rule = {"equal": {
        "condition": [
            {"equal": "=:100"}
        ],
        "queue": [
            {"equal": {}}
        ]
    }}

    actor = generate_actor(rule)
    one = Event("test")
    one.setData({"equal": "100"})
    actor.pool.queue.inbox.put(one)
    assert int(getter(actor.pool.queue.equal).data["equal"]) == 100


def test_list_membership():

    rule = {"list_membership": {
        "condition": [
            {"list_membership": "in:test"}
        ],
        "queue": [
            {"list_membership": {}}
        ]
    }}

    actor = generate_actor(rule)
    one = Event("test")
    one.setData({"list_membership": ["one", "test", "two"]})
    actor.pool.queue.inbox.put(one)
    assert "one" in getter(actor.pool.queue.list_membership).data["list_membership"]


def test_negative_list_membership():

    rule = {"list_membership": {
        "condition": [
            {"list_membership": "!in:test"}
        ],
        "queue": [
            {"list_membership": {}}
        ]
    }}

    actor = generate_actor(rule)
    one = Event("test")
    one.setData({"list_membership": ["one", "three", "two"]})
    actor.pool.queue.inbox.put(one)
    assert "test" not in getter(actor.pool.queue.list_membership).data["list_membership"]

#     match.stop()
