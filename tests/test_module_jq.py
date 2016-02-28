#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_jq.py
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
from wishbone.module.wb_jq import JQ
from wishbone.actor import ActorConfig
from utils import getter
import shutil
import os
import yaml


def dumpFile(d):

    try:
        shutil.rmtree('./test_rules')
    except Exception:
        pass
    try:
        os.makedirs('./test_rules')
    except Exception:
        pass

    with open('./test_rules/rule_1.yaml', 'w') as f:
        f.write(yaml.dump(d, default_flow_style=False))


def test_module_jq_basic():

    condition = {
        "name": "test",
        "expression": '.greeting | test( "hello")',
        "queue": "outbox"
    }

    actor_config = ActorConfig('jq', 100, 1, {}, "")
    jq = JQ(actor_config, conditions=[condition])

    jq.pool.createQueue('outbox')
    jq.pool.queue.inbox.disableFallThrough()
    jq.pool.queue.outbox.disableFallThrough()
    jq.start()

    e = Event({"greeting": "hello"})

    jq.pool.queue.inbox.put(e)
    one = getter(jq.pool.queue.outbox)
    assert one.get() == {"greeting": "hello"}


def test_module_jq_payload():

    condition = {
        "name": "test",
        "expression": '.greeting | test( "hello")',
        "queue": "outbox",
        "payload": {
            '@tmp.one': 1
        }
    }

    actor_config = ActorConfig('jq', 100, 1, {}, "")
    jq = JQ(actor_config, conditions=[condition])

    jq.pool.createQueue('outbox')
    jq.pool.queue.inbox.disableFallThrough()
    jq.pool.queue.outbox.disableFallThrough()
    jq.start()

    e = Event({"greeting": "hello"})

    jq.pool.queue.inbox.put(e)
    one = getter(jq.pool.queue.outbox)
    assert one.get('@tmp.one') == 1


def test_module_jq_bad_jq_expression():

    condition = {
        "name": "test",
        "expression": '.greeting | bad_test( "hello")',
        "queue": "outbox"
    }

    actor_config = ActorConfig('jq', 100, 1, {}, "")
    jq = JQ(actor_config, conditions=[condition])

    jq.pool.queue.inbox.disableFallThrough()
    jq.pool.queue.no_match.disableFallThrough()
    jq.start()

    e = Event({"greeting": "hello"})

    jq.pool.queue.inbox.put(e)
    one = getter(jq.pool.queue.no_match)
    assert one.get() == {"greeting": "hello"}


def test_module_jq_valid_jq_expression_no_bool():

    condition = {
        "name": "test",
        "expression": '.greeting',
        "queue": "outbox"
    }

    actor_config = ActorConfig('jq', 100, 1, {}, "")
    jq = JQ(actor_config, conditions=[condition])

    jq.pool.queue.inbox.disableFallThrough()
    jq.pool.queue.no_match.disableFallThrough()
    jq.start()

    e = Event({"greeting": "hello"})

    jq.pool.queue.inbox.put(e)
    one = getter(jq.pool.queue.no_match)
    assert one.get() == {"greeting": "hello"}


def test_module_jq_disk_rule_basic():

    condition = {
        "expression": '.greeting | test("hello")',
        "queue": "outbox"
    }

    dumpFile(condition)

    actor_config = ActorConfig('jq', 100, 1, {}, "")
    jq = JQ(actor_config, location="./test_rules")

    jq.pool.queue.inbox.disableFallThrough()
    jq.pool.createQueue("outbox")
    jq.pool.queue.outbox.disableFallThrough()
    jq.start()

    e = Event({"greeting": "hello"})

    jq.pool.queue.inbox.put(e)
    one = getter(jq.pool.queue.outbox)
    assert one.get() == {"greeting": "hello"}


def test_module_jq_disk_rule_reload():

    condition = {
        "expression": '.greeting | test("hello")',
        "queue": "outbox"
    }

    dumpFile(condition)

    actor_config = ActorConfig('jq', 100, 1, {}, "")
    jq = JQ(actor_config, location="./test_rules")

    jq.pool.queue.inbox.disableFallThrough()
    jq.pool.queue.no_match.disableFallThrough()
    jq.start()

    condition2 = {
        "expression": '.greeting | test( "hi")',
        "queue": "outbox"
    }
    dumpFile(condition2)

    e = Event({"greeting": "hi"})

    jq.pool.queue.inbox.put(e)
    one = getter(jq.pool.queue.no_match)
    assert one.get() == {"greeting": "hi"}
