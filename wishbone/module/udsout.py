#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  udsout.py
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


class UDSOut(Actor):

    '''**Writes events to a Unix Domain Socket.**


    Parameters:

        - path(str)("/tmp/wishbone")
           |  The unix domain socket to write events to.

        - delimiter(str)("")
            |  The delimiter to use between each event.

    Queues:

        - inbox
           |  Incoming events.

    '''

    def __init__(self, actor_config, path="/tmp/wishbone", delimiter=""):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        self.sendToBackground(self.setupConnection)

    def consume(self, event):
        if isinstance(event.data, list):
            data = self.kwargs.delimiter.join(event.data)
        else:
            data = event.data

        self.socket.send(str(data) + self.kwargs.delimiter)

    def setupConnection(self):
        while self.loop():
            try:
                self.socket.sendall('')
                sleep(1)
            except Exception as err:
                while self.loop():
                    try:
                        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.socket.connect(self.kwargs.path)
                        self.logging.info("Connected to %s." % (self.kwargs.path))
                        break
                    except Exception as err:
                        self.logging.error("Failed to connect to %s. Reason: %s" % (self.kwargs.path, err))
                        sleep(1)
