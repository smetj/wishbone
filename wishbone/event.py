#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  event.py
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

from copy import deepcopy
from collections import namedtuple
import arrow


class Container():
    pass


class Namespace():
    pass


class Module():

    def __init__(self, name):
        self.name = name
        self.header = Container()
        self.data = None
        self.error = Container()


Metric = namedtuple("WishboneMetric", "time type source name value unit tags")
Log = namedtuple("WishboneLog", "time level pid module message")


class Event(object):

    '''
    **The Wishbone event object representation.**

    A class object containing the event data being passed from one Wishbone
    module to the other.
    '''

    def __init__(self, data=None):

        self.data = {
            "@timestamp": arrow.now(),
            "@version": 1,
            "@data": data,
            "@tmp": {
            },
            "@errors": {
            }
        }

    def clone(self):
        '''
        Returns a cloned version of the event using deepcopy.
        '''

        return deepcopy(self)

    def copy(self, source, destination):
        '''
        Copies the source key to the destination key.

        :param str source: The name of the source key.
        :param str destination: The name of the destination key.
        '''

        self.set(destination, deepcopy(self.get(source)))

    def delete(self, key=None):
        '''
        Deletes a key.

        :param str key: The name of the key to delete
        '''

        if key is None:
            self.data = None
        else:
            key = '.'.join(key.split('.')[:-1])
            self.set(key, None)

    def get(self, key="@data"):
        '''
        Returns the value of <key>.

        :param str key: The name of the key to read.
        :return: The value of <key>
        '''

        def travel(path, d):

            if len(path) == 1:
                if isinstance(d, dict):
                    return d[path[0]]
                else:
                    raise Exception()
            else:
                return travel(path[1:], d[path[0]])
        if key is None:
            return self.data
        else:
            path = key.split('.')
            try:
                return travel(path, self.data)
            except:
                raise KeyError(key)

    def set(self, value, key="@data"):
        '''
        Sets the value of <key>.

        :param value: The value to set.
        :param str key: The name of the key to assign <value> to.
        '''

        if key.startswith('@') and key not in ["@data", "@tmp", "@error", "@version"]:
            raise Exception("Keys starting with @ are reserved.")
        result = value
        for name in reversed(key.split('.')):
            result = {name: result}
        self.data.update(result)

    def dump(self, complete=False, convert_timestamp=True):
        '''
        Dumps the content of the event.

        :param bool complete: Determines whether to include @tmp and @errors.
        :param bool convert_timestamp: When True converts <Arrow> object to iso8601 string.
        :return: The content of the event.
        :rtype: dict
        '''

        d = {}
        for key, value in self.data.iteritems():
            if key == "@tmp" and not complete:
                continue
            if key == "@errors" and not complete:
                continue
            elif isinstance(value, arrow.arrow.Arrow) and convert_timestamp:
                d[key] = str(value)
            else:
                d[key] = value

        return d

    raw = dump
