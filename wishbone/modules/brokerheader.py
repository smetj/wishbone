#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       brokerheader.py
#
#       Copyright 2012 Jelle Smet development@smetj.net
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

from wishbone.toolkit import PrimitiveActor


class BrokerHeader(PrimitiveActor):
    '''**A Wishbone module which adds a wishbone.io_modules.broker header to each
    event**.

    When events go to the outside world via the boker module, it must know which
    exchange and routing key to use.  Typically one would connect this outbox queue
    to the outboxqueue of the wishbone.io_modules.broker instance.

    Parameters:

        - name (str):       The instance name when initiated.
        - key (str):        The routing key to use.
        - exchange (str):   The exchange to use.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    def __init__(self, name, key='wishbone', exchange=''):

        PrimitiveActor.__init__(self, name)
        self.key = key
        self.exchange = exchange

    def consume(self,doc):

        doc['header']['broker_key']=self.key
        doc['header']['broker_exchange']=self.exchange
        self.sendData(doc)

    def shutdown(self):

        self.logging.info('Shutdown')
