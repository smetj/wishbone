#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  graphite.py
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

from wishbone import Actor
from os.path import basename
from sys import argv
from os import getpid


class Graphite(Actor):

    '''**Converts the internal metric format to Graphite format.**

    Incoming metrics have following format:

        (time, type, source, name, value, unit, (tag1, tag2))
        (1381002603.726132, 'wishbone', 'hostname', 'queue.outbox.in_rate', 0, '', ())



    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - prefix(str)
           |  Some prefix to put in front of the metric name.

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

    def __init__(self, name, size=100, frequency=1, prefix='', script=True, pid=False, source=True):
        Actor.__init__(self, name, size, frequency)
        self.name = name
        self.prefix = prefix
        if script:
            self.script_name = '.%s' % (basename(argv[0]).replace(".py", ""))
        else:
            self.script_name = ''
        if pid:
            self.pid = "-%s" % (getpid())
        else:
            self.pid = ''

        self.source = source

        if self.source:
            self.doConsume = self.__consumeSource
        else:
            self.doConsume = self.__consumeNoSource

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        self.doConsume(event)

    def __consumeSource(self, event):

        new_event = self.createEvent()
        new_event.data = "%s%s%s%s.%s %s %s" % (self.prefix, event.data[2], self.script_name, self.pid, event.data[3], event.data[4], event.data[0])
        self.submit(new_event, self.pool.queue.outbox)

    def __consumeNoSource(self, event):

        new_event = self.createEvent()
        new_event.data = "%s%s%s.%s %s %s" % (self.prefix, self.script_name, self.pid, event.data[3], event.data[4], event.data[0])
        self.submit(event, self.pool.queue.outbox)
