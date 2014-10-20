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


class Header():

    def hasNamespace(self, namespace):

        if namespace in self.__dict__:
            return True
        else:
            return False


class NameSpace():

    def hasKey(self, key):

        if key in self.__dict__:
            return True
        else:
            return False


class Event():

    def __init__(self):
        self.header = Header()
        self.data = None
        self.time = int(time.time())
        self.uuid = str(uuid4())

    def getData(self):

        return self.data

    def getHeaderValue(self, namespace, key):

        if not self.header.hasNamespace(namespace):
            raise MissingNamespace("No namespace %s in event header." % (namespace))
        if not getattr(self.header, namespace).hasKey(key):
            raise MissingKey("No key %s in namespace %s" % (key, namespace))

        return self.header.__dict__[namespace].__dict__[key]

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
        for n in self.header.__dict__:
            header[n] = self.header.__dict__[n].__dict__

        return {"header": header, "data": self.data, "time": self.time, "uuid": self.uuid}

    def setHeaderKey(self, namespace, key, value):

        if not self.header.hasNamespace(namespace):
            self.setHeaderNamespace()
        self.header.__dict__[namespace].__dict__[key] = value

    def setHeaderNamespace(self, namespace):

        if not self.header.hasNamespace(namespace):
            self.header.__dict__[namespace] = NameSpace()
