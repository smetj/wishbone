#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  elasticsearchout.py
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
from gevent import spawn, sleep
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticSearchOut(Actor):

    '''**Submit data to Elasticsearch.**

    Submits data to Elasticsearch.

    Parameters:

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

    Queues:

        - inbox
           |  Incoming events submitted to the outside.

    '''

    def __init__(self, actor_config, hosts=[], use_ssl=False, verify_certs=False, index="wishbone", doc_type="wishbone"):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.__bulk = []

    def preHook(self):
        self.elasticsearch = Elasticsearch(self.kwargs.hosts, use_ssl=self.kwargs.use_ssl, verify_certs=self.kwargs.verify_certs)

    def consume(self, event):

        # todo(smetj): when data is of type list do bulk otherwise a regular insert. Rely on tipping bucket module for gathering.
        self.__bulk.append(event)

        if len(self.__bulk) > 100:
            bulk(self.elasticsearch, [{"_index": self.kwargs.index, "_type": self.kwargs.doc_type, "_source": event.data} for event in self.__bulk])
            self.__bulk = []
