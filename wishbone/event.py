#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  event.py
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
import time
from uuid import uuid4
from copy import deepcopy
from wishbone.error import MissingNamespace
from wishbone.error import MissingKey


class Container():

    def hasEntry(self, entry):

        if entry in self.__dict__:
            return True
        else:
            return False

    def getEntry(self, name):

        return self.__dict__[name]

    def setEntry(self, name, value):

        self.__dict__[name] = value


class Event():

    def __init__(self, namespace):
        self.header = Container()
        self.error = Container()
        self.data = None
        self.__data = None
        self.time = int(time.time())
        self.setHeaderNamespace(namespace)

    def getData(self):

        return self.data

    def getErrorValue(self, namespace):

        if not self.error.hasEntry(namespace):
            raise MissingNamespace("No namespace %s in errors." % (namespace))
        if not getattr(self.header, namespace).hasEntry(key):
            raise MissingKey("No error %s in errors %s" % (key, namespace))

    def getHeaderValue(self, namespace, key):

        if not self.header.hasEntry(namespace):
            raise MissingNamespace("No namespace %s in event header." % (namespace))
        if not getattr(self.header, namespace).hasEntry(key):
            raise MissingKey("No key %s in namespace %s" % (key, namespace))

        return self.header.__dict__[namespace].__dict__[key]

    def hasHeaderNamespace(self, namespace):

        return self.header.hasEntry(namespace)

    def hasHeaderKey(self, namespace, key):

        if not self.header.hasEntry(namespace):
            return False
        if not getattr(self.header, namespace).hasEntry(key):
            return False

        return True

    def clone(self, reference=False):

        if reference:
            return self
        else:
            e = deepcopy(self)
            e.uuid = str(uuid4())
            return e

    def raw(self):

        '''Returns a dictionary structure of the event.'''

        header = {}
        error = {}

        for n in self.header.__dict__:
            header[n] = self.header.__dict__[n].__dict__

        for n in self.error.__dict__:
            error[n] = self.error.__dict__[n].__dict__

        return {"header": header, "error": error, "data": self.data}

    def setData(self, data):

        self.data = data

    def setErrorValue(self, namespace, line, t, error):

        self.error.__dict__[namespace] = Container()
        self.error.__dict__[namespace].__dict__["line"] = line
        self.error.__dict__[namespace].__dict__["type"] = t
        self.error.__dict__[namespace].__dict__["error"] = error

    def setHeaderValue(self, namespace, key, value):

        self.header.__dict__[namespace].__dict__[key] = value

    def setHeaderNamespace(self, namespace):

        if not self.header.hasEntry(namespace):
            self.header.__dict__[namespace] = Container()
