#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  graphite.py
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

from wishbone import Actor
from wishbone.event import Metric
from os.path import basename
from sys import argv
from os import getpid


class Graphite(Actor):

    '''**Converts the internal metric format to Graphite format.**

    Incoming metrics have following format:

        See http://wishbone.readthedocs.org/en/1.1.0/logs%20and%20metrics.html#format
        for more information about the format.

        Available template variables are:

            time, source, name, value unit, prefix, script, pid, source

    Parameters:

        - template(str)('{prefix}.{source}.{script}.{pid}.{type}.{name} {value} {time}'):
            | The template to use to build the metric structure.
            | Python templates are used.

        - prefix(str)("wishbone"):
            |
    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, template="{prefix}.{source}.{script}.{type}.{name} {value} {time}", prefix='wishbone'):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")
        self.script = basename(argv[0]).replace(".py", "")
        self.pid = getpid()

    def consume(self, event):

        if isinstance(event.data, Metric):
            v = {"prefix": self.kwargs.prefix, "script": self.script, "pid": self.pid}
            v.update(event.data._asdict())
            event.setData(self.kwargs.template.format(**v))
            self.submit(event, self.pool.queue.outbox)
        else:
            self.logging.error("Metric dropped because not of type <wishbone.event.Metric>")
