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


class Namespace():

    def __init__(self):
        pass

    def addEntry(self, name):
        self.__dict__[name] = Entry()


class Entry():

    header = Container()
    data = Container()
    error = None

    def __init__(self, name):
        self.name = name


class Event():

    def __init__(self, namespace):
        self.instance = Namespace()
        self.last = None
        self.addNamespace(namespace)

    def addNamespace(self, namespace):
        self.instance.__dict__[namespace] = Entry(namespace)
        self.last = self.instance.__dict__[namespace]

    def listNamespace(self):
        for instance in self.instance.__dict__:
            yield self.instance.__dict__[instance]