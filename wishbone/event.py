#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  event.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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

import arrow
import time
from wishbone.error import BulkFull, InvalidData

EVENT_RESERVED = ["@timestamp", "@version", "@data", "@tmp", "@errors"]


class Bulk(object):

    def __init__(self, max_size=None, delimiter="\n"):
        self.__events = []
        self.max_size = max_size
        self.delimiter = delimiter
        self.error = None

    def append(self, event):
        '''
        Appends an event to the bulk object.
        '''

        if isinstance(event, Event):
            if self.max_size is None or len(self.__events) < self.max_size:
                self.__events.append(event)
            else:
                    raise BulkFull("Max number of events (%s) is reached." % (self.max_size))
        else:
            raise InvalidData()

    def dump(self):
        '''
        Returns an iterator returning all contained events
        '''

        for event in self.__events:
            yield event

    def dumpFieldAsList(self, field="@data"):
        '''
        Returns a list containing a specific field of each stored event.
        Events with a missing field are skipped.
        '''

        result = []
        for event in self.dump():
            try:
                result.append(event.get(field))
            except KeyError:
                pass
        return result

    def dumpFieldAsString(self, field="@data"):
        '''
        Returns a string joining <field> of each event with <self.delimiter>.
        Events with a missing field are skipped.
        '''

        result = []
        for event in self.dump():
            try:
                result.append(event.get(field))
            except KeyError:
                pass

        return self.delimiter.join(result)

    def size(self):
        '''
        Returns the number of elements stored in the bulk.
        '''

        return len(self.__events)


class Log(object):

    '''
    A Wishbone log object
    '''

    def __init__(self, time, level, pid, module, message):

        self.time = time
        self.level = level
        self.pid = pid
        self.module = module
        self.message = message

    def __str__(self):

        return "Log(%s)" % (self.__dict__)

    def __repr__(self):

        return "Log(%s)" % (self.__dict__)


class Metric(object):

    '''
    A Wishbone metric object
    '''

    def __init__(self, time, type, source, name, value, unit, tags):

        self.time = time
        self.type = type
        self.source = source
        self.name = name
        self.value = value
        self.unit = unit
        self.tags = tags

    def __str__(self):

        return "Metric(%s)" % (self.__dict__)

    def __repr__(self):

        return "Metric(%s)" % (self.__dict__)

    def dump(self):

        return self.__dict__


class Event(object):

    '''
    **The Wishbone event object representation.**

    A class object containing the event data being passed from one Wishbone
    module to the other.
    '''

    def __init__(self, data=None):

        self.data = {
            "@timestamp": time.time(),
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

        c = self.deepish_copy(self.data)
        e = Event()
        e.data = c
        return e

    def copy(self, source, destination):
        '''
        Copies the source key to the destination key.

        :param str source: The name of the source key.
        :param str destination: The name of the destination key.
        '''

        self.set(self.deepish_copy(self.get(source)), destination)

    def delete(self, key=None):
        '''
        Deletes a key.

        :param str key: The name of the key to delete
        '''

        s = key.split('.')
        if s[0] in EVENT_RESERVED and len(s) == 1:
            raise Exception("Cannot delete root of reserved keyword '%s'." % (key))

        if key is None:
            self.data = None
        else:
            if '.' in key:
                s = key.split('.')
                key = '.'.join(s[:-1])
                del(self.get(key)[s[-1]])
            else:
                del(self.data[key])

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
        if key is None or key is "" or key is ".":
            return self.data
        else:
            try:
                path = key.split('.')
                return travel(path, self.data)
            except:
                raise KeyError(key)

    def has(self, key="@data"):
        '''
        Returns a boot indicating the event has <key>

        :param str key: The name of the key to check
        :return: Bool
        '''

        try:
            self.get(key)
        except KeyError:
            return False
        else:
            return True

    def set(self, value, key="@data"):
        '''
        Sets the value of <key>.

        :param value: The value to set.
        :param str key: The name of the key to assign <value> to.
        '''

        if key.startswith('@') and key.split('.')[0] not in EVENT_RESERVED:
            raise Exception("Keys starting with @ are reserved.")
        result = value
        for name in reversed(key.split('.')):
            result = {name: result}

        self.dict_merge(self.data, result)
        # self.data.update(result)

    def dump(self, complete=False, convert_timestamp=True):
        '''
        Dumps the content of the event.

        :param bool complete: Determines whether to include @tmp and @errors.
        :param bool convert_timestamp: When True converts <Arrow> object to iso8601 string.
        :return: The content of the event.
        :rtype: dict
        '''

        d = {}
        for key, value in list(self.data.items()):
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

    def dict_merge(self, dct, merge_dct):

        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.

        Stolen from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9

        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        for k, v in list(merge_dct.items()):
            if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict):
                self.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    def deepish_copy(self, org):
        '''
        much, much faster than deepcopy, for a dict of the simple python types.

        Blatantly ripped off from https://writeonly.wordpress.com/2009/05/07
        /deepcopy-is-a-pig-for-simple-data/
        '''

        if isinstance(org, dict):
            out = dict().fromkeys(org)
            for k, v in list(org.items()):
                try:
                    out[k] = v.copy()   # dicts, sets
                except AttributeError:
                    try:
                        out[k] = v[:]   # lists, tuples, strings, unicode
                    except TypeError:
                        out[k] = v      # ints

            return out
        else:
            return org
