#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  udpin.py
#
#  Copyright 2015 Jelle Smet development@smetj.net
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
from gevent.server import DatagramServer


class UDPIn(Actor):

    '''**A UDP server.**

    A UDP server.

    Parameters:

        - address(string)("0.0.0.0")
           |  The address to bind to.

        - port(int)(19283)
           |  The port to listen on.

        - reuse_port(bool)(False)
           |  Whether or not to set the SO_REUSEPORT socket option.
           |  Allows multiple instances to bind to the same port.
           |  Requires Linux kernel >= 3.9

    Queues:

        - outbox
           |  Incoming events.

    '''

    def __init__(self, actor_config, address="0.0.0.0", port=19283):
        Actor.__init__(self, actor_config)

        self._address = address
        self.port = port

        self.pool.createQueue("outbox")
        self.server = DatagramServer("%s:%s" % (address, port), self.handle)

    def handle(self, data, address):
        '''Is called upon each incoming message'''

        event = self.createEvent()
        event.data = data
        self.submit(event, self.pool.queue.outbox)

    def preHook(self):
        self.logging.info('Started listening on %s:%s' % (self._address, self.port))
        self.server.start()

