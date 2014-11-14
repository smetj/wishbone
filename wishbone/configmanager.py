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
            yield self.__dict__[item]


class ListContainer(list):
    pass


class Arguments(object):

    def __init__(self, **kwargs):
        self.__values = kwargs
        self.__setattr__ = self.__readOnly

    def __readOnly(self, obj, value):
        raise Exception("Arguments is a read only object")

    def __getattr__(self, obj, objtype=None):

        if hasattr(self.__values[obj], '__call__'):
            return self.__values[obj]()
        else:
            return self.__values[obj]

    def __repr__(self):
        a = ["%s='%s'" % (item, self.__values[item]) for item in sorted(self.__values)]
        return "Arguments(%s)" % ", ".join(a)

    def __iter__(self):
        for x in self.__values:
            yield x


class Source(object):
    pass


class Destination(object):
    pass


class Module(object):

    def __init__(self, name, module, arguments):

        self.name = name
        self.module = module
        self.arguments = Arguments(**arguments)


class Route(namedtuple('Route', 'source_module source_queue destination_module destination_queue'), object):
    pass


class WishboneConfig(namedtuple('WishboneConfig', 'modules routes')):
    pass


class ConfigurationFactory(object):

    def __init__(self):

        self.lookup_methods = {}

    def factory(self, name, *args, **kwargs):

        # import the requested factory and initialize
        m = importlib.import_module(name)
        self.source = m.Config(*args, **kwargs)

        # initialize all defined lookup modules
        self.initializeLookupModules()

        modules = Container()
        for (name, module, arguments) in self.source.listModules():

            args_incl_lookups = self.replaceLookupDefsWithFunctions(arguments)
            setattr(modules, name, Module(name, module, args_incl_lookups))

        routes = ListContainer()
        for source_module, source_queue, destination_module, destination_queue in self.source.listRoutes():
            routes.append(Route(source_module, source_queue, destination_module, destination_queue))

        return WishboneConfig(modules, routes)

    def initializeLookupModules(self):

        for (name, module, arguments) in self.source.listLookups():
            m = importlib.import_module(module)
            self.lookup_methods[name] = m.Config(**arguments)

    def replaceLookupDefsWithFunctions(self, args):

        for arg in args:
            if isinstance(args[arg], str) and args[arg].startswith('~'):
                (lookup, var) = self.__extractLookupDef(args[arg])
                args[arg] = self.lookup_methods[lookup].generateLookup(var)

        return args

    def __extractLookupDef(self, e):

        m = re.match('~(.*?)\([\"|\'](.*)?[\"|\']\)', e)
        return (m.groups()[0], m.groups()[1])

