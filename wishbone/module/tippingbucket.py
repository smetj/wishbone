#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tippingbucket.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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
from wishbone.event import Bulk
from wishbone.error import BulkFull
from gevent import sleep


class TippingBucket(Actor):

    '''**Aggregates multiple events into bulk.**

    Aggregates multiple incoming events into bulk usually prior to submitting
    to an output module.

    Flushing the buffer can be done in various ways:

      - The age of the bucket exceeds <bucket_age>.
      - The size of the bucket reaches <bucket_size>.
      - Any event arrives in queue <flush>.


    Parameters:

        - bucket_size(int)(100)
           |  The maximum amount of events per bucket.

        - bucket_age(int)(10)
           |  The maximum age in seconds before a bucket is closed and
           |  forwarded.  This actually corresponds the time since the first
           |  event was added to the bucket.


    Queues:

        - inbox
           |  A description of the queue

        - outbox
           |  A description of the queue

        - flush

           |  Flushes the Bulk on receive messages despite the bulk being full
           |  or expired.

    '''

    def __init__(self, actor_config, bucket_size=100, bucket_age=10):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("flush")
        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.messageFlusher, "flush")

    def preHook(self):

        self.createEmptyBucket()
        self.sendToBackground(self.flushBucket)

    def consume(self, event):

        try:
            self.bucket.append(event)
        except BulkFull:
            self.logging.info("Bucket full after %s events.  Forwarded." % (self.kwargs.bucket_size))
            self.submit(self.bucket, self.pool.queue.outbox)
            self.bucket = Bulk(self.kwargs.bucket_size)
            self.bucket.append(event)

    def createEmptyBucket(self):

        self.bucket = Bulk(self.kwargs.bucket_size)
        self.resetTimer()

    def flushBucket(self):

        while self.loop():
            sleep(1)
            self._timer -= 1
            if self._timer == 0:
                if self.bucket.size > 0:
                    self.logging.info("Bucket age expired after %s s.  Forwarded." % (self.kwargs.bucket_age))
                    self.submit(self.bucket, self.pool.queue.outbox)
                    self.createEmptyBucket()
                else:
                    self.resetTimer()

    def messageFlusher(self, event):

        self.logging.info("Recieved message in <flush> queue.  Flushing bulk.")
        self.submit(self.bucket, self.pool.queue.outbox)
        self.createEmptyBucket()

    def resetTimer(self):

        self._timer = self.kwargs.bucket_age


