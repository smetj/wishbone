#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcpout.py
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
from gevent import socket


class UDPOut(Actor):

    '''**A UDP client which writes data to an UDP socket.**

    Writes data to an UDP socket.

    When <data> is of type list, all elements
    will be joined using <delimiter> and submitted together.

    Parameters:

        - host(string)("localhost")
           |  The host to submit to.

        - port(int)(19283)
           |  The port to submit to.

        - delimiter(str)("\\n")
           |  A delimiter to add to each event.


    Queues:

        - inbox
           |  Incoming events submitted to the outside.

    '''

    def __init__(self, actor_config, host="127.0.0.1", port=19283, delimiter="\n"):
        Actor.__init__(self, actor_config)

        self.host = host
        self.port = port
        self.delimiter = delimiter

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def consume(self, event):
        if isinstance(event.data, list):
            data = ''.join(event.data)
        else:
            data = event.data
        self.socket.sendto(str(data), (self.host, self.port))
