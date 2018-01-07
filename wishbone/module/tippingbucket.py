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


class Bucket(object):

    def __init__(self, key, size, age, logging, queue, looplock):

        self.key = key
        self.size = size
        self.age = age
        self.logging = logging
        self.queue = queue
        self.loop = looplock

        self.bucket = None
        self.createEmptyBucket()
        self.logging.info("Created new bucket with aggregation key '%s'." % (self.key))

    def createEmptyBucket(self):
        self.bucket = Bulk(self.size)
        self.resetTimer()

    def flushBucketTimer(self):

        '''
        Flushes the buffer when <bucket_age> has expired.
        '''

        while self.loop():
            sleep(1)
            self._timer -= 1
            if self._timer == 0:
                if self.bucket.size() > 0:
                    self.logging.debug("Bucket age expired after %s s." % (self.age))
                    self.flush()
                else:
                    self.resetTimer()

    def flush(self):
        '''
        Flushes the buffer.
        '''
        self.logging.debug("Flushed bucket '%s' of size '%s'" % (self.key, self.bucket.size()))
        self.queue.put(self.bucket)
        self.createEmptyBucket()

    def resetTimer(self):
        '''
        Resets the buffer expiry countdown to its configured value.
        '''

        self._timer = self.age


class TippingBucket(Actor):

    '''**Aggregates multiple events into bulk.**

    Aggregates multiple incoming events into bulk usually prior to submitting
    to an output module.

    Flushing the buffer can be done in various ways:

      - The age of the bucket exceeds <bucket_age>.
      - The size of the bucket reaches <bucket_size>.
      - Any event arrives in queue <flush>.


    Parameters::

        - bucket_size(int)(100)
           |  The maximum amount of events per bucket.

        - bucket_age(int)(10)
           |  The maximum age in seconds before a bucket is closed and
           |  forwarded.  This actually corresponds the time since the first
           |  event was added to the bucket.

        - aggregation_key(str)("default")
           |  Groups events with key <aggregation_key> into the same buckets.

    Queues::

        - inbox
           |  Incoming events

        - outbox
           |  Outgoing bulk events

        - flush
           |  Flushes the buffer on incoming events despite the bulk being
           |  full (bucket_size) or expired (bucket_age).

    '''

    def __init__(self, actor_config, bucket_size=100, bucket_age=10, aggregation_key="default"):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("flush")
        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.flushIncomingMessage, "flush")

        self.buckets = {}

    def consume(self, event):

        try:
            self.getBucket(self.kwargs.aggregation_key).bucket.append(event)
        except BulkFull:
            self.logging.debug("Bucket full after %s events." % (self.kwargs.bucket_size))
            self.getBucket(self.kwargs.aggregation_key).flush()
            self.getBucket(self.kwargs.aggregation_key).bucket.append(event)

    def getBucket(self, key):

        if key in self.buckets:
            return self.buckets[key]
        else:
            self.buckets[key] = Bucket(
                self.kwargs.aggregation_key,
                self.kwargs.bucket_size,
                self.kwargs.bucket_age,
                self.logging,
                self.pool.queue.outbox,
                self.loop)
            self.sendToBackground(self.buckets[key].flushBucketTimer)
            return self.buckets[key]

    def flushIncomingMessage(self, event):
        '''
        Called on each incoming messages of <flush> queue.
        Flushes the buffer.
        '''

        self.logging.debug("Recieved message in <flush> queue.  Flushing all bulk buffers.")
        for index, bucket in self.buckets:
            bucket.flush()
