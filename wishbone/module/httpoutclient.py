#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  httpoutclient.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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
import grequests


class HTTPOutClient(Actor):

    '''**Posts data to the requested URL**

    Posts data to a remote URL


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - method(str)("PUT")
           |  The http method to use. PUT/POST

        - content_type(str)("application/json")
           |  The content type to use.

        - accept(str)("text/plain")
           |  The accept value to use.

        - url(str)("http://localhost")
           |  The url to submit the data to

        - username(str)
           |  The username to authenticate

        - password(str)
           |  The password to authenticate


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, name, size, frequency, method="PUT", content_type="application/json", accept="text/plain", url="https://localhost", username=None, password=None):

        Actor.__init__(self, name)
        self.name = name
        self.method = method
        self.content_type = content_type
        self.accept = accept
        self.url = url
        self.username = username
        self.password = password

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        if self.method == "PUT":
            self.submitToResource = self.__put
        elif self.method == "POST":
            self.submitToResource = self.__post
        else:
            raise Exception("Invalid http method defined: '%s'." % self.method)

    def consume(self, event):

        try:
            response = self.submitToResource(event["data"])
            response.raise_for_status()
        except Exception as err:
            self.logging.error("Failed to submit data.  Reason: %s" % (err))
            raise

    def __put(self, data):

        return grequests.put(self.url, data=data, auth=(self.username, self.password), headers={'Content-type': self.content_type, 'Accept': self.accept}).send()

    def __post(self, data):

        return grequests.post(self.url, data=data, auth=(self.username, self.password), headers={'Content-type': self.content_type, 'Accept': self.accept}).send()
