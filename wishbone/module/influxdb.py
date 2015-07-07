#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  influxdb.py
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


class InfluxDB(Actor):

    '''**Converts the internal metric format to InfluxDB line format.**

    Incoming metrics have following format:

        (time, type, source, name, value, unit, (tag1, tag2))
        (1381002603.726132, 'wishbone', 'hostname', 'queue.outbox.in_rate', 0, '', ())



    Parameters:

        - script(bool)(True)
           |  Include the script name.

        - pid(bool)(False)
           |  Include pid value in script name.

        - source(bool)(True):
           |  Include the source name in the naming schema.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")
        self.tags = {}

    def consume(self, event):

        if isinstance(event.data, Metric):
            event.setData(self.generate(event.data))
            self.submit(event, self.pool.queue.outbox)
        else:
            self.logging.error("Metric dropped because not of type <wishbone.event.Metric>")

    def generate(self, data):

        return "%s source=%s,module=%s,queue=%s value=%s %s" % (data.name, data.source, data.module, data.queue, data.value, data.time)
