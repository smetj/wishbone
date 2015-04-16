#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  loglevelfilter.py
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


class LogLevelFilter(Actor):

    '''**Filters log events based on loglevel.**

    Drops internal Wishbone logs based on loglevel.

    Internal Wishbone format:

    (6, 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')


    Parameters:

        - loglevel(int)(6)
           |  The maximum allowed loglevel.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, loglevel=6):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consumer, "inbox")

    def consumer(self, event):

        if event.data[0] <= self.kwargs.loglevel:
            self.submit(event, self.pool.queue.outbox)
