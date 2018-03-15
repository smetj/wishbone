#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  throughput.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from wishbone.actor import Actor
from wishbone.module import OutputModule
from gevent import sleep


class Throughput(OutputModule):
    '''
    Prints the number of messages passing through on STDOUT.


    Parameters::

        - selection(str)("data")
           |  The event key to submit.

        - payload(str)(None)
           |  The string to submit.
           |  If defined takes precedence over `selection`.

        - native_events(bool)(False)
           |  If True, outgoing events are native events.

        - parallel_streams(int)(1)
           |  The number of outgoing parallel data streams.

    Queues::

        - inbox
           |  incoming events
    '''

    def __init__(self, actor_config,
                 selection=None, payload=None, native_events=False, parallel_streams=1,
                 *args, **kwargs):

        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.sendToBackground(self.calculateSpeed)
        self.counter = 0

    def consume(self, event):

        self.counter += 1

    def calculateSpeed(self):

        self.last = 0

        while self.loop():
            print("Events per second passing through: %s" % (self.counter - self.last))
            self.last = self.counter
            sleep(1)
