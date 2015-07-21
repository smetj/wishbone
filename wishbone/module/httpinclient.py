#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       httpinclient.py
#
#       Copyright 2015 Jelle Smet development@smetj.net
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

from gevent import monkey; monkey.patch_socket()
import requests

from wishbone import Actor
from gevent import sleep


class HTTPInClient(Actor):

    '''**A HTTP client doing http requests to pull data in.**

    This module requests an URL at the defined interval.


    Parameters:

        - url(str/list)("http://localhost")
           |  The URL to fetch (including port).
           |  When a list, will process all urls defined.

        - username(str)(None)
           |  The login to use.

        - password(str)(None)
           |  The password to use.

        - interval(int)(60)
           |  The interval in seconds between each request.


   Queues:

        - outbox
           |  Incoming events


    The header contains:

        - status_code:          The status code of the request.

    '''

    def __init__(self, actor_config, url="http://localhost", username=None, password=None, interval=60):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("outbox")

    def preHook(self):
        if isinstance(self.kwargs.url, list):
            for url in self.kwargs.url:
                self.sendToBackground(self.scheduler, url)
        else:
            self.sendToBackground(self.scheduler, self.kwargs.url)

    def scheduler(self, url):
        while self.loop():
            event = self.createEvent()
            event.data = None
            try:
                response = requests.get(url, auth=(self.kwargs.username, self.kwargs.password))
            except Exception as err:
                self.logging.warn("Problem requesting resource.  Reason: %s" % (err))
                sleep(1)
            else:
                event.setHeaderValue("status_code", response.status_code)
                event.setHeaderValue("url", url)
                event.data = response.text
                self.submit(event, self.pool.queue.outbox)
                sleep(self.kwargs.interval)
