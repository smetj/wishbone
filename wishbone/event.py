#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  event.py
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

import time
from wishbone.error import BulkFull, InvalidData, TTLExpired
from uuid import uuid4
from jinja2 import Template
from copy import deepcopy
from scalpl import Cut
from easydict import EasyDict


EVENT_RESERVED = ["timestamp", "data", "tmp", "errors", "uuid", "uuid_previous", "cloned", "bulk", "ttl", "tags"]


def extractBulkItemValues(event, selection):
    '''Yields a field from all events in the bulk event.

    Args:

        event (wishbone.event.Event): The wishbone event in bulk mode.
        selection (str): The field to extract form each event in the bulk.


    Yields:

        str/int/float/dict/list: The value of the event
    '''

    if event.isBulk():
        for e in event.data["data"]:
            yield Event().slurp(e).get(selection)


def extractBulkItems(event):
    '''Yields all the events from a bulk event.

    Args:

        event (wishbone.event.Event): The wishbone event in bulk mode.

    Yields:

        `wishbone.event.Event`: The value of the event
    '''

    if event.isBulk():
        for e in event.data["data"]:
            yield Event().slurp(e)


class Event(object):

    '''The Wishbone event object.

    A class object containing the event data being passed from one Wishbone
    module to the other.

    The keyformat used is the one handled by the ``Scalpl`` module
    (https://pypi.python.org/pypi/scalpl/).

    Args:

        data (dict/list/string/int/float): The data to assign to the ``data`` field.
        ttl (int): The TTL value for the event.
        bulk (bool): Initialize the event as a bulk event
        bulk_size (int): The number of events the bulk can hold.

    Attributes:

        data (dict): A dict containing the event data structure.
        bulk_size (int): The max allowed bulk size.
    '''

    def __init__(self, data=None, ttl=254, bulk=False, bulk_size=100):

        self.data = Cut({
            "cloned": False,
            "bulk": bulk,
            "data": None,
            "errors": {
            },
            "tags": [],
            "timestamp": time.time(),
            "tmp": {
            },
            "ttl": ttl,

            "uuid_previous": [
            ],
        })

        if bulk:
            self.data["data"] = []
        else:
            self.set(data)
        self.data["uuid"] = str(uuid4())
        self.bulk_size = bulk_size

    def appendBulk(self, event):
        '''Appends an event to this bulk event.

        Args:

            event(wishbone.event.Event): The event to add to the bulk instance

        Raises:

            InvalidData: Either the event is not of type Bulk or ``event`` is
                         not an wishbone.event.Event instance.
        '''

        if self.data["bulk"]:
            if isinstance(event, Event):
                if len(self.data["data"]) == self.bulk_size:
                    raise BulkFull("The bulk event already contains '%s' events." % (self.bulk_size))

                self.data["data"].append(event.dump())
            else:
                raise InvalidData("'event' should be of type wishbone.event.Event.")
        else:
            raise InvalidData("This instance is not initialized as a bulk event.")

    def clone(self):
        '''Returns a cloned version of the event.

        Returns:

            class: A ````wishbone.event.Event```` instance


        '''
        e = deepcopy(self)

        if "uuid_previous" in e.data:
            e.data["uuid_previous"].append(
                e.data["uuid"]
            )
        else:
            e.data["uuid_previous"] = [
                e.data["uuid"]
            ]
        e.data["uuid"] = str(uuid4())
        e.data["timestamp"] = time.time()
        e.data["cloned"] = True

        return e

    def copy(self, source, destination):
        '''Copies the source key to the destination key.

        Args:

            source (str): The name of the source key.
            destination (str): The name of the destination key.
        '''

        self.set(
            deepcopy(
                self.get(
                    source
                )
            ),
            destination
        )

    def decrementTTL(self):
        '''Decrements the TTL value.

        Raises:

            TTLExpired: When TTL has reached 0.
        '''

        self.data["ttl"] -= 1

        if self.data["ttl"] <= 0:
            raise TTLExpired("Event TTL expired in transit.")

    def delete(self, key=None):
        '''Deletes a key.

        Args:

            key (str): The key to delete

        Raises:

            Exception: Deleting the root of a reserved keyword such as ``data`` or ``tags``.
            KeyError: When a non-existing key is referred to.
        '''

        s = key.split('.')
        if s[0] in EVENT_RESERVED and len(s) == 1:
            raise Exception("Cannot delete root of reserved keyword '%s'." % (key))

        del(self.data[key])

    def dump(self):
        '''
        Dumps the complete event.
        This complete event is also called a ``native event``

        Returns:

            dict: The content of the event.
        '''

        d = deepcopy(self)
        d.data["timestamp"] = float(d.data["timestamp"])
        return d.data.data

    def get(self, key="data"):
        '''Returns the value of ``key``.

        ``key`` must be in ``Scalpl`` format.

        Args:

            key (str): The name of the key to read.

        Returns:

            str/int/float/dict/list: The value of the key

        Raises:

            KeyError: The provided key does not exist.
        '''
        if key in [None, "", "."]:
            return self.data
        else:
            try:
                return self.data[key]
            except Exception as err:
                raise KeyError(key)

    def has(self, key="data"):
        '''Returns a bool indicating the event has ``key``

        ``key`` must be in ``Scalpl`` format.

        Args:

            key (str): The name of the key to check

        Returns:

            bool: True if the key is there otherwise false

        Raises:

            KeyError: The provided key does not exist
        '''

        try:
            self.data[key]
        except KeyError:
            return False
        else:
            return True

    def isBulk(self):
        '''Tells whether event is ``bulk`` or not.


        Returns:

            bool: True if the event is bulk

        '''

        return self.data["bulk"]

    def merge(self, value, key="data"):
        '''
        Merges value into ``key``.
        Value types should be mergeable otherwise an error is returned.

        Args:
            value (dict,list): The value to merge
            key (str): The key to merge into

        Raises:
            InvalidData: Types are not mergeable
        '''

        try:
            if isinstance(value, list):
                self.data[key] += value
            elif isinstance(value, dict):
                self.data[key].update(value)
            else:
                raise InvalidData("Source and destination are incompatible to merge")
        except Exception:
            raise InvalidData("Source and destination are incompatible to merge")

    def render(self, template, env_template=None):
        '''Returns a formatted string using the provided template and key

        Args:

            template (str): A string representing the Jinja2 template.
            env_template (``jinja2.Environment``): Used to render template strings from.
                If not set, then template rendering happens without environment.

        Returns:

            str: The rendered string

        Raises:

            InvalidData: An invalid jinja2 template has been provided
        '''

        try:
            if env_template is None:
                return Template(template).render(self.dump())
            else:
                return env_template.from_string(template).render(self.dump())
        except Exception as err:
            raise InvalidData("Failed to render template. Reason: %s" % (err))

    def renderField(self, field_name, env_template=None):
        '''
        Expects ``field_name`` to contain a template, renders it and replaces
        its content with the result. If the field ``field_name`` contains
        anything else than a string then it's silently ignored.

        Args:

            field_name (str): A string defining the field to handle.

        Returns:

            None

        Raises:

            InvalidData: An invalid jinja2 template has been provided
        '''

        try:
            raw_value = self.get(field_name)
            rendered_value = self.__renderDataStructure(raw_value, env_template)
            self.set(rendered_value, field_name)
        except Exception as err:
            raise InvalidData("Failed to render template. Reason: %s" % (err))

    def renderKwargs(self, template_kwargs):
        '''
        Renders all the templates found in ``template_kwargs`` and sets
        self.kwarg, a version of the current module's kwargs relate to this
        events' content

        Args:

            template_kwargs (dict): A dict of the modules kwargs optoinally
                                    containing Template instances.
        '''

        def recurse(data):

            if isinstance(data, Template):
                try:
                    return data.render(**self.dump())
                except Exception as err:
                    return "#error: %s#" % (err)
            elif isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    result[key] = recurse(value)
                return EasyDict(result)
            elif isinstance(data, list):
                result = []
                for value in data:
                    result.append(recurse(value))
                return result
            else:
                return data

        self.kwargs = EasyDict(
            recurse(
                template_kwargs
            )
        )

    def set(self, value, key="data"):
        '''Sets the value of ``key``.

        ``key`` must be in ``Scalpl`` format.

        Args:

            value (str, int, float, dict, list): The value to assign.
            key (str): The key to store the value
        '''

        self.data[key] = value

    def slurp(self, data):
        '''
        Create an event object from a ``native event`` dict exported by
        ``dump()``

        The timestamp field will be reset to the time this method has been
        called.


        Args:

            data (dict): The dict object containing the complete event.


        Returns:

            wishbone.event.Event: A Wishbone event instance.


        Raises:

            InvalidData:  ``data`` does not contain valid fields to build
                                  an event
        '''
        try:
            assert isinstance(data, (dict, Cut)), "event.slurp() expects a dict."
            for item in [
                ("timestamp", float),
                ("data", None),
                ("tmp", dict),
                ("errors", dict),
                ("uuid", str),
                ("uuid_previous", list),
                ("cloned", bool),
                ("bulk", bool),
                ("ttl", int),
                ("tags", list)
            ]:
                assert item[0] in data, "%s is missing" % (item[0])
                if item[1] is not None:
                    assert isinstance(data[item[0]], item[1]), "%s type '%s' is not valid." % (item[0], item[1])
        except AssertionError as err:
            raise InvalidData("The incoming data could not be used to construct an event.  Reason: '%s'." % err)
        else:
            self.data = Cut(data)
            self.data["timestamp"] = time.time()

        return(self)

    raw = dump

    def __renderDataStructure(self, datastructure, env_template):

        def recurse(data):

            if isinstance(data, str):
                try:
                    if env_template is None:
                        return Template(data).render(**self.dump())
                    else:
                        return env_template.from_string(data).render(**self.dump())
                except Exception as err:
                    return "#error: %s#" % (err)
            elif isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    result[key] = recurse(value)
                return EasyDict(result)
            elif isinstance(data, list):
                result = []
                for value in data:
                    result.append(recurse(value))
                return result
            else:
                return data

        return recurse(datastructure)
