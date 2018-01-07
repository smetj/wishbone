#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  py2devtools.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
#
#
# The MIT License (MIT)

# Copyright (c) 2014 Nylas

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Original source https://github.com/nylas/nylas-perftools/blob/master/py2devtools.py


import json
import sys
import timeit
import gevent
from os import getpid


class Node(object):
    def __init__(self, name, id_):
        self.name = name
        self.id_ = id_
        self.children = {}
        self.hitCount = 1

    def serialize(self):
        res = {
            'functionName': self.name,
            'hitCount': self.hitCount,
            'children': [c.serialize() for c in list(self.children.values())],
            'scriptId': '1',
            'url': '',
            'lineNumber': 1,
            'columnNumber': 1,
            'deoptReason': '',
            'id': self.id_,
            'callUID': self.id_
        }
        return res

    def add(self, frames, idgen):
        if not frames:
            self.hitCount += 1
            return
        head = frames[0]
        child = self.children.get(head)
        if child is None:
            child = Node(name=head, id_=idgen())
            self.children[head] = child
        child.add(frames[1:], idgen)


class Profiler(object):
    def __init__(self, target_greenlet=None, interval=0.0001):
        if target_greenlet is not None:
            self.target_greenlet_id = id(target_greenlet)
        else:
            self.target_greenlet_id = None
        self.interval = interval
        self.started = None
        self.last_profile = None
        self.root = Node('head', 1)
        self.nextId = 1
        self.samples = []
        self.timestamps = []

    def _idgenerator(self):
        self.nextId += 1
        return self.nextId

    def _profile(self, frame, event, arg):
        if event == 'call':
            self._record_frame(frame.f_back)

    def _record_frame(self, frame):
        if (self.target_greenlet_id is None or
                id(gevent.getcurrent()) == self.target_greenlet_id):
            now = timeit.default_timer()
            if self.last_profile is not None:
                if now - self.last_profile < self.interval:
                    return
            self.last_profile = now
            self.timestamps.append(int(1e6 * now))
            stack = []
            while frame is not None:
                stack.append(self._format_frame(frame))
                frame = frame.f_back
            stack.reverse()
            self.root.add(stack, self._idgenerator)
            self.samples.append(self.nextId)

    def _format_frame(self, frame):
        return '{}({})'.format(frame.f_code.co_name,
                               frame.f_globals.get('__name__'))

    def output(self):
        if not self.samples:
            return {}
        return json.dumps({
            'startTime': self.started,
            'endTime': 0.000001 * self.timestamps[-1],
            'timestamps': self.timestamps,
            'samples': self.samples,
            'head': self.root.serialize()
        })

    def __enter__(self):
        sys.setprofile(self._profile)
        self.started = timeit.default_timer()
        print("")
        print("########################################")
        print("#                                      #")
        print("# Wishbone is running in profile mode. #")
        print("# This has a performance impact.       #")
        print("#                                      #")
        print("########################################")
        print("")

    def __exit__(self, type, value, traceback):
        sys.setprofile(None)
        filename = './wishbone_%s_.cpuprofile' % getpid()
        with open(filename, 'w') as f:
            f.write(self.output())
            print(("Written profile file '%s'." % (filename)))
