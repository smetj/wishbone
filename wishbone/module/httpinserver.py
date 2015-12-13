#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       httpinserver.py
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

from wishbone import Actor
from wishbone.event import Event
from gevent import pywsgi
from gevent import socket
from gevent.pool import Pool
from wishbone.logging import MockLogger


class HTTPInServer(Actor):

    '''**Receive events over HTTP.**

    Creates an HTTP server to which events can be submitted.


    Parameters:

        - address(str)("0.0.0.0")
           |  The address to bind to.

        - port(int)(19283)
           |  The port to bind to.

        - keyfile(str)(None)
           |  When SSL is required, the location of the keyfile to use.

        - certfile(str)(None)
           |  When SSL is required, the location of the certfile to use.

        - ca_certs(str)(None)
            |  When SSL is required, the location of the ca certs to use.

        - delimiter(str)(None)
           |  The delimiter which separates multiple
           |  messages in a stream of data.

        - poolsize(int)(1000)
            |  The connection pool size.

        - so_reuseport(bool)(False)
            |  Enables socket option SO_REUSEPORT.
            |  See https://lwn.net/Articles/542629/
            |  Required when running multiple Wishbone instances.

    Queues:

        - outbox
           |  Incoming events submitted to /.


    When more queues are connected to this module instance, they are
    automatically mapped to the URL resource.

    For example http://localhost:10080/fubar is mapped to the <fubar> queue.
    The root resource "/" is mapped the <outbox> queue.
    '''

    def __init__(self, actor_config, address="0.0.0.0", port=19283, keyfile=None, certfile=None, ca_certs=None, delimiter=None, poolsize=1000, so_reuseport=False):
        Actor.__init__(self, actor_config)

        if self.kwargs.delimiter is None:
            self.delimit = self.__noDelimiter
        elif self.kwargs.delimiter == "\\n":
            self.delimit = self.__newLineDelimiter
        else:
            self.delimit = self.__otherDelimiter

        self.logger_info = MockLogger(self.name, self.pool.queue.logs, 6)
        self.logger_error = MockLogger(self.name, self.pool.queue.logs, 3)

    def preHook(self):
        self.sendToBackground(self.__serve)

    def consume(self, env, start_response):

        try:
            try:
                queue = self.__validateQueueName(env['PATH_INFO'])
            except Exception as err:
                start_response('404 Not Found', [('Content-Type', 'text/plain')])
                return "%s" % (err)

            if env["REQUEST_METHOD"] in ["PUT", "POST"]:
                counter = 0
                for line in self.delimit(env["wsgi.input"]):
                    event = Event(line)
                    self.submit(event, self.pool.getQueue(queue))
                    counter += 1
                start_response('200 OK', [('Content-Type', 'text/plain')])
                return "Submitted %s event(s) to queue '%s'." % (counter, queue)
            elif env["REQUEST_METHOD"] == "GET":
                start_response('200 OK', [('Content-Type', 'text/plain')])
                return "OK"
            else:
                start_response('405 Method Not Allowed', [('Content-Type', 'text/plain')])
                return "405 Method Not Allowed"
        except Exception as err:
            start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
            return "A problem occurred processing your request. Reason: %s" % (err)

    def __validateQueueName(self, path):

        '''Validates and returns a trimmed value.'''

        result = [x for x in path.split('/') if x != ""]
        if result == []:
            queue = "outbox"
        else:
            queue = result[0]

        if len(result) > 1:
            raise Exception("Endpoint can only have a depthlevel of 1.")
        elif not self.pool.hasQueue(queue):
            raise Exception("There is no queue with name %s." % (queue))
        else:
            return queue

    def __newLineDelimiter(self, data):
        for line in data.readlines():
            yield line.rstrip()

    def __noDelimiter(self, data):
        return ["".join(data.readlines())]

    def __otherDelimiter(self, data):
        r = []
        for line in data.readlines():
            if line.rstrip("\n").endswith(self.kwargs.delimiter):
                line = line.rstrip("\n")[:-len(self.kwargs.delimiter)]
                if line != "\n":
                    r.append(line)
                yield "".join(r)
                r = []
            else:
                r.append(line)
        yield "\n".join(r)

    def __serve(self):
        pool = Pool(self.kwargs.poolsize)
        if self.kwargs.keyfile is not None and self.kwargs.certfile is not None and self.kwargs.ca_certs is not None:
            self.__server = pywsgi.WSGIServer(
                self.getListener(),
                self.consume,
                spawn=pool,
                log=self.logger_info,
                error_log=self.logger_error,
                keyfile=self.kwargs.keyfile,
                certfile=self.kwargs.certfile,
                ca_certs=self.kwargs.ca_certs)
        else:
            self.__server = pywsgi.WSGIServer(
                self.getListener(),
                self.consume,
                spawn=pool,
                log=self.logger_info,
                error_log=self.logger_error)

        if self.kwargs.so_reuseport:
            self.__server.sock.setsockopt(socket.SOL_SOCKET, 15, 1)

        self.__server.start()
        self.logging.info("Serving on %s:%s with a connection poolsize of %s." % (self.kwargs.address, self.kwargs.port, self.kwargs.poolsize))

    def postHook(self):

        self.logging.info("Stopped serving.")
        self.__server.stop()

    def getListener(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if self.kwargs.so_reuseport:
            sock.setsockopt(socket.SOL_SOCKET, 15, 1)

        sock.setblocking(0)
        sock.bind((self.kwargs.address, self.kwargs.port))
        sock.listen(50)
        return sock

