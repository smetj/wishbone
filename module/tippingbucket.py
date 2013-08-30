#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       tippingbucket.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone import Actor
from time import time
from gevent import sleep, spawn
from gevent.event import Event

class TippingBucket(Actor):
    '''**A builtin Wishbone module which buffers data.**

    This module buffers data and dumps it to the output queue on 3 conditions:

        * Last data entered in buffer exceeds <age> seconds.
        * The length of the data in buffer exceeds <size> size.
        * Number of incoming events exceeds <events>.

    When the buffer is empty, the header of the first incoming message will be
    used as the header for the message going out containing the content of the
    buffer.  If you want to override that header with a predefined one then
    use the <predefined_header> option.

    Keep in mind to set at least one of the parameters otherwise buffering
    will be indefinite until your box runs out of memory


    Parameters:

        - age (int):    The time in seconds to buffer before flushing.
                        0 to disable. (default 0)
        - size (int):   The total size in bytes to buffer before flushing.
                        0 to disable. (default 0)
        - events (int): The total number of events to buffer before flushing.
                        0 to disable. (default 0)

        - predefined_header (dict): Assign this header to the buffered event
                                    when submitting to outbox.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    def __init__(self, name, age=0, size=0, events=0, predefined_header=None):

        Actor.__init__(self, name)
        self.age = age
        self.size = size
        self.events = events
        self.predefined_header=predefined_header
        self.buff=[]
        self.buff_age=0
        self.buff_size=0
        self.buff_events=0
        self.buff_header={}
        spawn(self.reaper)

    def consume(self,doc):

        self.buff_events+=1

        if self.buff_age==0:
            self.buff_age=time()
            self.header=doc["header"]

        self.buff.append(doc["data"])
        self.buff_size+=len((doc["data"]))

        if self.size > 0 and self.buff_size > self.size:
            self.logging.debug("Size of buffer (%s) exceeded. Flushed."%(self.size))
            self.flushBuffer()

        if self.events > 0 and self.buff_events > self.events:
            self.logging.debug("Total number of events (%s) in buffer exceeded. Flushed."%(self.events))
            self.flushBuffer()

    def reaper(self):
        '''Check whether our cache is expired and flush the buffer if its the case.'''

        while self.block():
            if self.buff_age != 0:
                if (float(time()) - float(self.buff_age)) > float(self.age):
                    self.flushBuffer()
                    self.logging.debug("Age of buffer exceeded %s seconds. Flushed."%(self.age))
            sleep(0.1)

    def flushBuffer(self):
        '''Flushes the buffer.'''

        if self.predefined_header == None:
            self.queuepool.outbox.put({"header":self.buff_header, "data":self.buff})
        else:
            self.queuepool.outbox.put({"header":self.predefined_header, "data":self.buff})
        self.resetBuffer()
        sleep()

    def resetBuffer(self):
        '''Resets the counters.'''

        self.buff=[]
        self.buff_age=0
        self.buff_size=0
        self.buff_events=0
        self.buff_header={}

    def shutdown(self):
        self.logging.info('Shutdown')