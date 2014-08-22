#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  namedpipein.py
#
#  Copyright 2014 Jelle Smet development@smetj.net
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
from gevent import spawn, sleep
from gevent import os as gevent_os

# from gevent import monkey;monkey.patch_all()
import os


class NamedPipeIn(Actor):

    '''**Takes data in from a named pipe..**

    Creates a named pipe and read data from it.

    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - path(str)("/tmp/wishbone")
           |  The the location of the named pipe.

    Queues:

        - outbox
           |  Data coming from the outside world.
    '''

    def __init__(self, name, size=100, frequency=1, path="/tmp/wishbone"):
        Actor.__init__(self, name, size, frequency)

        self.pool.createQueue("outbox")
        self.name = name
        self.path = path

    def preHook(self):

        os.mkfifo(self.path)
        self.logging.info('Named pipe %s created.' % (self.path))
        spawn(self.drain)

    def consume(self, event):
        for line in event:
            self.submit({"header": {}, "data": line}, self.pool.queue.outbox)

    def drain(self):
        '''Reads the named pipe.'''

        self.logging.info('Started.')
        fd = os.open(self.path, os.O_RDWR | os.O_NONBLOCK)
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
            os.unlink(self.path)
        except:
            pass
