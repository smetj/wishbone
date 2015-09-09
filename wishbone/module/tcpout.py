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
from gevent import sleep, socket


class TCPOut(Actor):

    '''**A TCP client which writes data to a TCP socket.**

    Writes data to a tcp socket.

    When <data> is of type list, all elements
    will be joined using <delimiter> and submitted together.

    Parameters:

        - host(string)("localhost")
           |  The host to submit to.

        - port(int)(19283)
           |  The port to submit to.

        - timeout(int)(1)
           |  The time in seconds to timeout when connecting

        - delimiter(str)("\\n")*
           |  A delimiter to add to each event.


    Queues:

        - inbox
           |  Incoming events submitted to the outside.

    '''

    def __init__(self, actor_config, host="127.0.0.1", port=19283, timeout=10, delimiter="\n"):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        self.sendToBackground(self.setupConnection)

    def setupConnection(self):

        while self.loop():
            try:
                self.socket.sendall('')
                sleep(1)
            except Exception as err:
                while self.loop():
                    try:
                        self.socket = socket.socket()
                        self.socket.settimeout(self.kwargs.timeout)
                        self.socket.connect((self.kwargs.host, self.kwargs.port))
                        self.logging.info("Connected to %s:%s." % (self.kwargs.host, self.kwargs.port))
                        break
                    except Exception as err:
                        self.logging.error("Failed to connect to %s:%s. Reason: %s" % (self.kwargs.host, self.kwargs.port, err))
                        sleep(1)

    def postHook(self):
        try:
            self.socket.close()
            self.logging.info("Connection closed to %s:%s" % (self.kwargs.host, self.kwargs.port))
        except:
            pass

    def consume(self, event):
        if isinstance(event.last.data, list):
            data = self.kwargs.delimiter.join(event.last.data)
        else:
            data = event.last.data
        self.socket.sendall(str(data) + self.kwargs.delimiter)
