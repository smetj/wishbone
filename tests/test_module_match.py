#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_match.py
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
from wishbone.module.match import Match
from wishbone.actor import ActorConfig
from utils import getter
from gevent import sleep


def generate_actor(rules):

    actor_config = ActorConfig('match', 100, 1, {}, "")
    match = Match(actor_config, rules=rules)

    match.pool.queue.inbox.disableFallThrough()
    for queue in rules.keys():
        match.pool.createQueue(queue)
        getattr(match.pool.queue, queue).disableFallThrough()

    match.start()
    return match


def test_file_load():

    import os
    import yaml
    import shutil

    os.mkdir('/tmp/wishbone_tests')
    actor_config = ActorConfig('match', 100, 1, {}, "")
    match = Match(actor_config, location="/tmp/wishbone_tests")
    match.pool.createQueue("file")
    match.pool.queue.file.disableFallThrough()
    match.pool.queue.inbox.disableFallThrough()

    #Test 1
    rule_1 = {
        "condition": [
            {"file": "re:.*?one.*"}
        ],
        "queue": [
            {"file": {}}
        ]
    }

    with open('/tmp/wishbone_tests/one.yaml', 'w') as one:
        one.write(yaml.dump(rule_1, default_flow_style=False))
    match.start()
    sleep(1)

    e = Event("test")
    e.set({"file": "zero one two"})
    match.pool.queue.inbox.put(e)

    assert getter(match.pool.queue.file).get()["file"] == "zero one two"

    # Test 2
    rule_2 = {
        "condition": [
            {"file": "re:.*?two.*"}
        ],
        "queue": [
            {"file": {}}
        ]
    }
    with open('/tmp/wishbone_tests/two.yaml', 'w') as one:
        one.write(yaml.dump(rule_2, default_flow_style=False))
    sleep(1)

    e = Event("test")
    e.set({"file": "one two three"})
    match.pool.queue.inbox.put(e)
    assert getter(match.pool.queue.file).get()["file"] == "one two three"
    shutil.rmtree('/tmp/wishbone_tests')


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
    e = Event({"regex": "one two three"})
    actor.pool.queue.inbox.put(e)
    assert getter(actor.pool.queue.regex).get()["regex"] == "one two three"


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
    e.set({"neg_regex": "one twwo three"})
    actor.pool.queue.inbox.put(e)
    assert getter(actor.pool.queue.neg_regex).get()["neg_regex"] == "one twwo three"


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
    e.set({"bigger": "100"})
    actor.pool.queue.inbox.put(e)
    assert getter(actor.pool.queue.bigger).get()["bigger"] == "100"


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
    one.set({"bigger_equal": "100"})
    two = Event("test")
    two.set({"bigger_equal": "101"})
    actor.pool.queue.inbox.put(one)
    actor.pool.queue.inbox.put(two)
    assert int(getter(actor.pool.queue.bigger_equal).get()["bigger_equal"]) == 100
    assert int(getter(actor.pool.queue.bigger_equal).get()["bigger_equal"]) > 100


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
    one.set({"smaller": "99"})
    actor.pool.queue.inbox.put(one)
    assert int(getter(actor.pool.queue.smaller).get()["smaller"]) < 100


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
    one.set({"smaller_equal": "100"})
    two = Event("test")
    two.set({"smaller_equal": "99"})
    actor.pool.queue.inbox.put(one)
    actor.pool.queue.inbox.put(two)
    assert int(getter(actor.pool.queue.smaller_equal).get()["smaller_equal"]) == 100
    assert int(getter(actor.pool.queue.smaller_equal).get()["smaller_equal"]) < 100


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
    one.set({"equal": "100"})
    actor.pool.queue.inbox.put(one)
    assert int(getter(actor.pool.queue.equal).get()["equal"]) == 100


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
    one.set({"list_membership": ["one", "test", "two"]})
    actor.pool.queue.inbox.put(one)
    assert "one" in getter(actor.pool.queue.list_membership).get()["list_membership"]


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
    one.set({"list_membership": ["one", "three", "two"]})
    actor.pool.queue.inbox.put(one)
    assert "test" not in getter(actor.pool.queue.list_membership).get()["list_membership"]
