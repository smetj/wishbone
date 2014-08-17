#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       httpin.py
#
#       Copyright 2014 Jelle Smet development@smetj.net
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
from gevent import pywsgi, spawn


class HTTPIn(Actor):

    '''**Receive events over HTTP.**

    Creates an HTTP server to which events can be submitted.


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - address(str)("0.0.0.0")
           |  The address to bind to.

        - port(int)(19283)
           |  The port to bind to.

        - keyfile(str)(None)
           |  When SSL is required, the location of the keyfile to use.

        - certfile(str)(None)
           |  When SSL is required, the location of the certfile to use.

        - delimiter(str)(None)
           |  The delimiter which separates multiple
           |  messages in a stream of data.

    Queues:

        - outbox
           |  Incoming events submitted to /.


    When more queues are connected to this module instance, they are
    automatically mapped to the URL resource.

    For example http://localhost:10080/fubar is mapped to the <fubar> queue.
    The root resource "/" is mapped the <outbox> queue.
    '''

    def __init__(self, name, size, frequency, address="0.0.0.0", port=19283, keyfile=None, certfile=None, delimiter=None):
        Actor.__init__(self, name, size, frequency)
        self.name = name
        self.address = address
        self.port = port
        self.keyfile = keyfile
        self.certfile = certfile
        self.delimiter = delimiter

        if self.delimiter is None:
            self.delimit = self.__noDelimiter
        elif self.delimiter == "\\n":
            self.delimit = self.__newLineDelimiter
        else:
            self.delimit = self.__otherDelimiter

    def preHook(self):
        spawn(self.__serve)

    def consume(self, env, start_response):
        try:
            for line in self.delimit(env["wsgi.input"]):
                if env['PATH_INFO'] == '/':
                    self.submit({"header": {}, "data": line}, self.pool.queue.outbox)
                else:
                    q = self.pool.getQueue(env['PATH_INFO'].lstrip('/'))
                    self.submit({"header": {}, "data": line}, q)
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return "OK"
        except Exception as err:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return "A problem occurred processing your request. Reason: %s" % (err)

    def __newLineDelimiter(self, data):
        for line in data.readlines():
            yield line.rstrip()

    def __noDelimiter(self, data):
        return ["".join(data.readlines())]

    def __otherDelimiter(self, data):
        r = []
        for line in data.readlines():
            if line.rstrip("\n").endswith(self.delimiter):
                line = line.rstrip("\n")[:-len(self.delimiter)]
                if line != "\n":
                    r.append(line)
                yield "".join(r)
                r = []
            else:
                r.append(line)
        yield "\n".join(r)

    def __setupQueues(self):
        return
        self.deleteQueue("inbox")
        for resource in self.resources:
            path = resource.keys()[0]
            queue = resource[resource.keys()[0]]
            self.createQueue(queue)
            self.queue_mapping[path] = getattr(self.queuepool, queue)

    def __serve(self):
        if self.keyfile is not None and self.certfile is not None:
            self.__server = pywsgi.WSGIServer(
                (self.address, self.port), self.consume, keyfile=self.keyfile, certfile=self.certfile)
        else:
            self.__server = pywsgi.WSGIServer(
                (self.address, self.port), self.consume, log=None)
        self.__server.start()
        self.logging.info("Serving on %s:%s" % (self.address, self.port))

    def postHook(self):

        self.logging.info("Stopped serving.")
        self.__server.stop()
