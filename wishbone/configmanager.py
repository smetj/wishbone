#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configmanager.py
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

from collections import namedtuple
import importlib
import re


class Container(object):

    def list(self):
        for item in self.__dict__:
            yield item


class ListContainer(list):
    pass


class Arguments(object):

    def __getattr__(self, name):

        return self.__dict__["__%s" % name]()

    def list(self):
        for item in self.__dict__:
            yield item

    def get(self, name):
        return self.__dict__[name]

    def set(self, name, value):
        self.__dict__[name] = value



class Source(object):
    pass


class Destination(object):
    pass


class Module(object):

    def __init__(self, name, module, arguments):

        self.name = name
        self.module = module
        self.arguments = Arguments()
        for argument in arguments:
            if hasattr(arguments[argument], '__call__'):
                self.arguments.__dict__["__%s" % argument] = arguments[argument]
            else:
                self.arguments.__dict__[argument] = arguments[argument]

class Route(object):

    def __init__(self, source_module, source_queue, destination_module, destination_queue):

        self.source = Source()
        self.source.module = source_module
        self.source.queue = source_queue

        self.destination = Destination()
        self.destination.module = destination_module
        self.destination.queue = destination_queue


class WishboneConfig(namedtuple('WishboneConfig', 'modules routes')):
    pass


class ConfigurationFactory(object):

    def __init__(self):

        self.lookup_methods = {}

    def factory(self, name, *args, **kwargs):

        m = importlib.import_module(name)
        self.source = m.Config(*args, **kwargs)

        self.initializeLookupModules()

        modules = Container()
        for (name, module, arguments) in self.source.listModules():
            for argument in arguments:
                arguments[argument] = self.replaceLookups(arguments[argument])
            setattr(modules, name, Module(name, module, arguments))

        routes = ListContainer()
        for source_module, source_queue, destination_module, destination_queue in self.source.listRoutes():
            routes.append(Route(source_module, source_queue, destination_module, destination_queue))

        return WishboneConfig(modules, routes)

    def initializeLookupModules(self):

        for (name, module, arguments) in self.source.listLookups():
            m = importlib.import_module(module)
            self.lookup_methods[name] = m.Config(**arguments)

    def replaceLookups(self, argument):

        if isinstance(argument, str) and argument.startswith('~'):
            (lookup, var) = self.__extractLookupDef(argument)
            return self.lookup_methods[lookup].generateLookup(var)
        else:
            argument

    def __extractLookupDef(self, e):

        m = re.match('~(.*?)\([\"|\'](.*)?[\"|\']\)', e)
        return (m.groups()[0], m.groups()[1])

