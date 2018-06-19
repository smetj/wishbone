#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_queueselect.py
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
from wishbone.module.queueselect import QueueSelect
from wishbone.actor import ActorConfig
from wishbone.queue import QueuePool
from wishbone.utils.test import getter


def test_module_queueselect_default():

    actor_config = ActorConfig('queueselect', QueuePool(), disable_exception_handling=True)

    template = {
        "name": "name of the rule",
        "queue": "{{ 'queue_1' if data.one == 1 else 'queue_2' }}",
        "payload": {
            "queue_1": {
                "detail_1": "some value",
                "detail_2": "some other value",
            },
            "queue_2": {
                "detail_1": "some value",
                "detail_2": "some other value",
            }
        }
    }

    queueselect = QueueSelect(actor_config, templates=[template])
    queueselect.pool.queue.inbox.disableFallThrough()
    queueselect.pool.queue.outbox.disableFallThrough()

    queueselect.pool.createQueue("queue_1")
    queueselect.pool.queue.queue_1.disableFallThrough()

    queueselect.pool.createQueue("queue_2")
    queueselect.pool.queue.queue_2.disableFallThrough()

    queueselect.start()

    queueselect.pool.queue.inbox.put(Event({"one": 1, "two": 2}))

    assert getter(queueselect.pool.queue.queue_1).get() == {"one": 1, "two": 2}

    queueselect.stop()


def test_module_queueselect_multiple_queues():

    actor_config = ActorConfig('queueselect', QueuePool(), disable_exception_handling=True)

    template = {
        "name": "name of the rule",
        "queue": "{{ 'queue_1,queue_2' if data.one == 1 else 'queue_2' }}",
        "payload": {
            "queue_1": {
                "detail_1": "some value",
                "detail_2": "some other value",
            },
            "queue_2": {
                "detail_1": "some value",
                "detail_2": "some other value",
            }
        }
    }

    queueselect = QueueSelect(actor_config, templates=[template])
    queueselect.pool.queue.inbox.disableFallThrough()
    queueselect.pool.queue.outbox.disableFallThrough()

    queueselect.pool.createQueue("queue_1")
    queueselect.pool.queue.queue_1.disableFallThrough()

    queueselect.pool.createQueue("queue_2")
    queueselect.pool.queue.queue_2.disableFallThrough()

    queueselect.start()

    queueselect.pool.queue.inbox.put(Event({"one": 1, "two": 2}))

    assert getter(queueselect.pool.queue.queue_1).get() == {"one": 1, "two": 2}
    assert getter(queueselect.pool.queue.queue_2).get() == {"one": 1, "two": 2}

    queueselect.stop()


def test_module_queueselect_nomatch():

    actor_config = ActorConfig('queueselect', QueuePool(), disable_exception_handling=True)

    template = {
        "name": "name of the rule",
        "queue": "{{ 'queue_1,queue_2' if data.one == 1 else 'queue_2' }}",
        "payload": {
            "queue_1": {
                "detail_1": "some value",
                "detail_2": "some other value",
            },
            "queue_2": {
                "detail_1": "some value",
                "detail_2": "some other value",
            }
        }
    }

    queueselect = QueueSelect(actor_config, templates=[template])
    queueselect.pool.queue.inbox.disableFallThrough()
    queueselect.pool.queue.outbox.disableFallThrough()
    queueselect.pool.queue.nomatch.disableFallThrough()

    queueselect.start()

    queueselect.pool.queue.inbox.put(Event({"one": "one", "two": "two"}))
    assert getter(queueselect.pool.queue.nomatch).get() == {"one": "one", "two": "two"}

    queueselect.stop()


def test_module_queueselect_regex():

    actor_config = ActorConfig('queueselect', QueuePool(), disable_exception_handling=True)

    template = {
        "name": "name of the rule",
        "queue": "{{ 'queue_1' if regex('\d', data.one) else 'queue_2' }}",
        "payload": {
            "queue_1": {
                "detail_1": "some value",
                "detail_2": "some other value",
            },
            "queue_2": {
                "detail_1": "some value",
                "detail_2": "some other value",
            }
        }
    }

    queueselect = QueueSelect(actor_config, templates=[template])
    queueselect.pool.queue.inbox.disableFallThrough()
    queueselect.pool.queue.outbox.disableFallThrough()
    queueselect.pool.queue.nomatch.disableFallThrough()

    queueselect.start()

    queueselect.pool.queue.inbox.put(Event({"one": 1, "two": "two"}))
    assert getter(queueselect.pool.queue.nomatch).get() == {"one": 1, "two": "two"}

    queueselect.stop()


def test_module_queueselect_novalidqueue():

    actor_config = ActorConfig('queueselect', QueuePool(), disable_exception_handling=True)

    templates = [
        {
            "name": "rule_1",
            "queue": "{{ 'no_such_queue_1' if data.one == 1 else 'no_such_queue_2' }}",
        },
        {
            "name": "rule_2",
            "queue": "{{ 'no_such_queue_1' if data.one == 1 else 'no_such_queue_2' }}",
        }
    ]

    queueselect = QueueSelect(actor_config, templates=templates)
    queueselect.pool.queue.inbox.disableFallThrough()
    queueselect.pool.queue.outbox.disableFallThrough()
    queueselect.pool.queue.nomatch.disableFallThrough()

    queueselect.pool.createQueue("queue_1")
    queueselect.pool.queue.queue_1.disableFallThrough()

    queueselect.pool.createQueue("queue_2")
    queueselect.pool.queue.queue_2.disableFallThrough()

    queueselect.start()

    queueselect.pool.queue.inbox.put(Event({"one": 1, "two": 2}))

    assert getter(queueselect.pool.queue.nomatch).get() == {"one": 1, "two": 2}

    queueselect.stop()
