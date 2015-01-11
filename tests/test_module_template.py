#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_template.py
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

from wishbone.event import Event
from wishbone.module import Template
from wishbone.actor import ActorConfig
from os import unlink

from utils import getter

def test_module_template_header():

    '''Tests template defined in header.'''

    actor_config = ActorConfig('template', 100, 1)
    template = Template(actor_config, header_templates=["test.header.hello"])

    template.pool.queue.inbox.disableFallThrough()
    template.pool.queue.outbox.disableFallThrough()
    template.start()

    e = Event('test')
    e.setHeaderValue("hello", "The numerical representation of one is {{one}}", "test")
    e.setData({"one": 1})

    template.pool.queue.inbox.put(e)
    one=getter(template.pool.queue.outbox)
    assert one.getHeaderValue('test', "hello") == "The numerical representation of one is 1"

def test_module_template_file():

    '''Tests template defined in file.'''

    with open ("template.tmpl", "w") as f:
        f.write("The numerical representation of one is {{one}}")

    actor_config = ActorConfig('template', 100, 1)
    template = Template(actor_config, template="template.tmpl")

    template.pool.queue.inbox.disableFallThrough()
    template.pool.queue.outbox.disableFallThrough()
    template.start()

    e = Event('test')
    e.setHeaderValue("hello", "The numerical representation of one is {{one}}", "test")
    e.setData({"one": 1})

    template.pool.queue.inbox.put(e)
    one=getter(template.pool.queue.outbox)
    unlink('template.tmpl')

    assert one.data == "The numerical representation of one is 1"

