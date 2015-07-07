#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  namedpipein.py
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
from gevent import sleep
from gevent import os as gevent_os

# from gevent import monkey;monkey.patch_all()
import os


class NamedPipeIn(Actor):

    '''**Takes data in from a named pipe..**

    Creates a named pipe and read data from it.

    Parameters:

        - path(str)("/tmp/wishbone")
           |  The the location of the named pipe.

    Queues:

        - outbox
           |  Data coming from the outside world.
    '''

    def __init__(self, actor_config, path="/tmp/wishbone"):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("outbox")

    def preHook(self):

        os.mkfifo(self.kwargs.path)
        self.logging.info('Named pipe %s created.' % (self.kwargs.path))
        self.sendToBackground(self.drain, self.kwargs.path)

    def consume(self, event):
        for line in event:
            e = self.createEvent()
            e.data = line
            self.submit(e, self.pool.queue.outbox)

    def drain(self, p):
        '''Reads the named pipe.'''

        self.logging.info('Started.')
        fd = os.open(p, os.O_RDWR | os.O_NONBLOCK)
        gevent_os.make_nonblocking(fd)

        while self.loop():
            try:
                lines = gevent_os.nb_read(fd, 4096).splitlines()
                if len(lines) == 0:
                    sleep(0.5)
                else:
                    self.consume(lines)
            except OSError:
                pass

    def postHook(self):

        try:
            os.unlink(self.kwargs.path)
        except:
            pass
