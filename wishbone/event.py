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


Metric = namedtuple("WishboneMetric", "time source module queue name value tags")
Log = namedtuple("WishboneLog", "time level pid module message")

class Event(object):

    '''
    **The Wishbone event object representation.**

    A class object containing the event data being passed from one Wishbone
    module to the other.
    '''

    def __init__(self, namespace):
        self.module = Namespace()
        self.initNamespace(namespace)
        self.last = self.module.__dict__[namespace]
        self.__source_queue = None
        self.__source_namespace = None

    def clone(self):
        '''
        returns a deep copy instance of the event.
        '''

        return deepcopy(self)

    def initNamespace(self, namespace):
        '''
        Initializes an empty event namespace.
        Usually this is the module's instance name to which to which the event
        arrives.
        '''

        if namespace not in self.module.__dict__:
            self.module.__dict__[namespace] = Module(namespace)
        self.current_namespace = namespace

    def getData(self, namespace, clone=False):
        '''
        Returns the data value of the requested namespace.
        When clone is True, a deepcopied version is returned.
        '''

        if clone:
            return deepcopy(self.module.__dict__[namespace].data)
        else:
            return self.module.__dict__[namespace].data

    def getHeaderValue(self, namespace, key, clone=False):
        '''
        Returns the header values of the requested namespace.
        When clone is True, a deepcopied version is returned.
        '''

        return self.module.__dict__[namespace].header.__dict__[key]

    def listNamespace(self):
        '''
        Returns a generator returning over all registered namespace
        instances.
        '''

        for module in self.module.__dict__:
            yield self.module.__dict__[module]

    def lookupHeaderValue(self, name, clone=False):
        '''
        Returns the header value using dotted format.
        When clone is True, a deepcopied version is returned.
        '''

        (namespace, key) = name.split('.')
        return self.getHeaderValue(namespace, key, clone)

    def raw(self):
        '''
        Returns a dictionary representation of the event.
        '''

        data = {}
        for module in self.listNamespace():
            data[module.name] = {"header": module.header.__dict__, "data": module.data, "error": module.error.__dict__}
        return data

    def rollBackEvent(self):

        '''When invoked resubmits this event to the queue it came from'''

        if self.__source_queue is None or self.__source_namespace is None:
            pass
        else:
            del (self.module.__dict__[self.current_namespace])
            self.current_namespace = self.__source_namespace
            self.__source_queue.put(self)

    def setSource(self, queue):

        self.__source_namespace = self.current_namespace
        self.__source_queue = queue

    def setData(self, data):
        '''
        Sets the data value of the requested namespace.
        '''

        self.module.__dict__[self.current_namespace].data = data
        self.last = self.module.__dict__[self.current_namespace]

    def setErrorValue(self, line, error_type, error_value):
        '''Sets the error value for the current namespace.'''

        self.module.__dict__[self.current_namespace].error.line = line
        self.module.__dict__[self.current_namespace].error.type = error_type
        self.module.__dict__[self.current_namespace].error.type = error_value

    def setHeaderValue(self, key, value, namespace=None):
        '''Sets the header value of the requested namespace.

        When <namespace> has value <None> then the current namespace is used.
        '''

        if namespace is None:
            namespace = self.current_namespace
        else:
            if namespace not in self.module.__dict__:
                self.module.__dict__[namespace] = Module(namespace)

        self.module.__dict__[namespace].header.__dict__[key] = value

    def __getLastData(self):
        return self.last.data

    data = property(__getLastData, setData)