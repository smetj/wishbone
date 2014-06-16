#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tcpout.py
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
from gevent import sleep, spawn, socket


class TCPOut(Actor):

    '''**A Wishbone ouput module which writes data to a TCP socket.**

    Writes data to a tcp socket.

    Parameters:

        - name (str):       The instance name when initiated.

        - host (string):    The host to submit to.
                            Default: "localhost"

        - port (int):       The port to submit to.
                            Default: 19283

        - timeout(int):     The time in seconds to timeout when
                            connecting
                            Default: 1

        - delimiter(str):   A delimiter to add to each event.
                            Default: "\\n"

    Queues:

        - inbox:    Incoming events submitted to the outside.

    '''

    def __init__(self, name, size=100, host="127.0.0.1", port=19283, timeout=10, delimiter="\n"):
        Actor.__init__(self, name, size)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout
        self.delimiter = delimiter

    def preHook(self):
        spawn(self.setupConnection)

    def setupConnection(self):

        while self.loop():
            try:
                self.socket.sendall('')
                sleep(1)
            except Exception as err:
                while self.loop():
                    try:
                        self.socket = socket.socket()
                        self.socket.settimeout(self.timeout)
                        self.socket.connect((self.host, self.port))
                        self.logging.info("Connected to %s:%s." % (self.host, self.port))
                        break
                    except Exception as err:
                        self.logging.error("Failed to connect to %s:%s. Reason: %s" % (self.host, self.port, err))
                        sleep(1)

    def postHook():
        try:
            self.socket.close()
            self.logging.info("Connection closed to %s:%s" % (self.host, self.port))
        except:
            pass

    def consume(self, event):

        if isinstance(event["data"], list):
            data = self.delimiter.join(event["data"])
        else:
            data = event["data"]
        self.socket.sendall(str(data)+self.delimiter)
