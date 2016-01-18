#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  elasticsearchout.py
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
from wishbone.error import QueueFull
from gevent import sleep
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticSearchOut(Actor):

    '''**Submit data to Elasticsearch.**

    Submits data to Elasticsearch.

    Documents are indexed in bulk.  The number of messages per bulk insert is
    alligned to --queue-size.  If a number of messages sit in the buffer for
    longer than <interval> seconds, the buffer will be flushed despite not
    reaching the --queue-size number of messages.

    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - hosts(list)(["localhost:9200"])
           |  A list of "hostname:port" strings.

        - use_ssl(bool)(False)
           |  When enable expects SSL connectivity

        - verify_certs(bool)(False)
           |  When using SSL do certificate verification

        - index(str)("wishbone")
           |  The name of the index

        - doc_type(str)("wishbone")
           |  The document type

        - interval(int)(5)
           |  The buffer time flush interval.

    Queues:

        - inbox
           |  Incoming events submitted to the outside.

    '''

    def __init__(self, actor_config, selection="@data", hosts=["localhost:9200"], use_ssl=False, verify_certs=False, index="wishbone", doc_type="wishbone", interval=5):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.pool.createQueue("bulk")
        self.pool.queue.bulk.disableFallThrough()
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        self.elasticsearch = Elasticsearch(self.kwargs.hosts, use_ssl=self.kwargs.use_ssl, verify_certs=self.kwargs.verify_certs)
        self.sendToBackground(self.__flushTimer)

    def consume(self, event):

        try:
            self.pool.queue.bulk.put(event)
        except QueueFull:
            self.pool.queue.inbox.rescue(event)
            self.logging.debug("Flushing batch of %s docs after reaching batch size." % (self.pool.queue.bulk.size()))
            self.flush()

    def flush(self):
        bulk(self.elasticsearch, [{"_index": self.kwargs.index, "_type": self.kwargs.doc_type, "_source": e.get(self.kwargs.selection)} for e in self.pool.queue.bulk.dump()])

    def __flushTimer(self):

        while self.loop():
            sleep(self.kwargs.interval)
            if self.pool.queue.bulk.size() > 0:
                self.logging.debug("Flushing batch of %s docs after reaching timeout." % (self.pool.queue.bulk.size()))
                self.flush()
