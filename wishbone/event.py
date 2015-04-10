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


class Event(object):

    def __init__(self, namespace):
        self.module = Namespace()
        self.initNamespace(namespace)
        self.last = self.module.__dict__[namespace]

    def clone(self):
        '''returns a deep copy instance of the event.'''

        return deepcopy(self)

    def initNamespace(self, namespace):
        '''Initializes an empty namespace.'''

        if namespace not in self.module.__dict__:
            self.module.__dict__[namespace] = Module(namespace)
        self.current_namespace = namespace

    def listNamespace(self):
        '''Returns a generator iterating over all registered namespaces.'''

        for module in self.module.__dict__:
            yield self.module.__dict__[module]

    def getData(self, namespace):

        '''Returns the data of the requested namespace.'''

        return self.module.__dict__[namespace].data

    def __getLastData(self):
        return self.last.data

    def setData(self, data):
        '''Sets the data field of the requested namespacec.'''

        self.module.__dict__[self.current_namespace].data = data
        self.last = self.module.__dict__[self.current_namespace]

    def getHeaderValue(self, namespace, key):
        '''Returns the header value of the requested namespace.'''

        return self.module.__dict__[namespace].header.__dict__[key]

    def lookupHeaderValue(self, name):
        '''Returns the header value using dotted format.'''

        (namespace, key) = name.split('.')
        return self.module.__dict__[namespace].header.__dict__[key]

    def raw(self):
        '''returns a dictionary representation of the event.'''

        data = {}
        for module in self.listNamespace():
            data[module.name] = {"header": module.header.__dict__, "data": module.data, "error": module.error.__dict__}
        return data

    def setHeaderValue(self, key, value, namespace=None):
        '''Sets a header value of the requested namespace.'''

        if namespace == None:
            namespace = self.current_namespace
        else:
            if namespace not in self.module.__dict__:
                self.module.__dict__[namespace] = Module(namespace)

        self.module.__dict__[namespace].header.__dict__[key] = value

    def setErrorValue(self, line, error_type, error_value):
        '''Sets the error value for namespace.'''

        self.module.__dict__[self.current_namespace].error.line = line
        self.module.__dict__[self.current_namespace].error.type = error_type
        self.module.__dict__[self.current_namespace].error.type = error_value

    data = property(__getLastData, setData)