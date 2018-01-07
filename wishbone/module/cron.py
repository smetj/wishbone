#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cron.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from gevent import monkey; monkey.patch_all()
from wishbone.actor import Actor
from wishbone.event import Event
from wishbone.module import InputModule
from wishbone.protocol.decode.dummy import Dummy
from cronex import CronExpression
from gevent import sleep
import time


class Cron(InputModule):

    '''**Generates an event at the defined time**

    Generates an event with the defined payload at the chosen time.
    Time is in crontab format.


    Parameters::

        - cron(string)("*/10 * * * *")
            | The cron expression.

        - payload(str)("wishbone")
            | The content of <destination>.

        - destination(str)("data")
            | The location to write <payload> to.


    Queues::

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, cron="*/10 * * * *", payload="wishbone", destination="data"):

        Actor.__init__(self, actor_config)
        self.pool.createQueue("outbox")
        self.cron = CronExpression("%s wishbone" % self.kwargs.cron)
        self.decode = Dummy().handler

    def preHook(self):
        self.sendToBackground(self.timer)

    def timer(self):
        while self.loop():
            if self.cron.check_trigger(time.localtime(time.time())[:5]):
                self.logging.info("Cron executed.")
                event = Event()
                event.renderKwargs(self.kwargs_template)
                for payload in self.decode(event.kwargs.payload):
                    event.set(payload, event.kwargs.destination)
                    self.submit(event, "outbox")
            sleep(60)
