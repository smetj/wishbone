#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  namedpipe.py
#
#  Copyright 2012 Jelle Smet development@smetj.net
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

from gevent import spawn, Greenlet, sleep
from gevent.queue import Queue
from wishbone.toolkit import QueueFunctions, Block
import os
import sys
import logging
import gevent.core


class NamedPipe(Greenlet, QueueFunctions, Block):
    '''**A Wishbone IO module which accepts external input from a named pipe.**

    Creates a named pipe to which data can be submitted.

    Parameters:

        - name (str):       The instance name when initiated.
        - path (str):       The absolute path of the named pipe.

    Queues:

        - inbox:    Data coming from the outside world.
    '''

    def __init__(self, name, path):
        Greenlet.__init__(self)
        QueueFunctions.__init__(self)
        Block.__init__(self)
        self.name=name
        self.logging = logging.getLogger( name )
        self.path = path
        self.logging.info('Initialiazed.')
        os.mkfifo ( self.path )
        self.logging.info('Named pipe %s created.'%(self.path))

    def _run(self):
        self.logging.info('Started.')
        try:
            fd = os.open(self.path, os.O_RDONLY|os.O_NONBLOCK)
        except Exception as err:
            self.logging.error('Error opening Named pipe %s. Reason: %s' % (self.path, err))
        else:
            try:
                while self.block() == True:
                    sleep(0)
                    try:
                        lines = os.read(fd, 4096).splitlines()
                    except:
                        pass
                    if lines:
                        self.logging.debug('Received a chunk of 4096 bytes.')
                        for line in lines:
                            self.putData({'header':{},'data':line}, queue='inbox')
                    else:
                        self.wait(0.1)

            except KeyboardInterrupt:
                self.fifo.close()
                self.shutdown()
            except Exception as err:
                self.logging.warn(err)

    def shutdown(self):
        os.unlink(self.path)
        self.logging.info('Shutdown')
