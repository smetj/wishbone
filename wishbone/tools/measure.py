#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  timer.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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

from time import time

class Measure(object):

    @classmethod
    def runTime(cls, fn):

        """Decorator function which keeps track of the number of calls and the
        time it takes to execute the function."""

        def do(self, *args, **kwargs):
            t = time()
            result = fn(self, *args, **kwargs)
            elapsed=time()-t
            try:
                self.metrics[fn.__name__]
            except:
                self.metrics[fn.__name__]={"total_time":0,"hits":0}
            self.metrics[fn.__name__]["total_time"] += round(elapsed,6)
            self.metrics[fn.__name__]["hits"] += 1
            return result
        return do

    def runTimeConsume(self, fn, data):
        t = time()
        result = fn(data)
        elapsed=time()-t
        try:
            self.metrics[fn.__name__]
        except:
            self.metrics[fn.__name__]={"total_time":0,"hits":0}
        self.metrics[fn.__name__]["total_time"] += round(elapsed,6)
        self.metrics[fn.__name__]["hits"] += 1
        return result