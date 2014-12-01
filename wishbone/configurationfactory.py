#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configurationfactory.py
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

from wishbone.error import ModuleInitFailure
from collections import namedtuple
import importlib
import re


class Lookup(object):

    def __init__(self, fn):

        self.__fn = fn

    def __str__(self):

        return self.__fn()

    def __repr__(self):

        return self.__fn()


class Arguments(object):

    def __init__(self, **kwargs):
        self.__values = kwargs
        self.__setattr__ = self.__readOnly

    def __readOnly(self, obj, value):
        raise Exception("Arguments is a read only object")

    def __getattr__(self, obj, objtype=None):
        return self.__values[obj]

    def __repr__(self):
        a = ["%s='%s'" % (item, self.__values[item]) for item in sorted(self.__values)]
        return "Arguments(%s)" % ", ".join(a)

    def __iter__(self):
        for x in self.__values:
            yield x


class Module(object):

    def __init__(self, instance, module, arguments):

        '''Wishbone configuration representation of a Module.

        Parameters:

            - instance(str)     : module instance name.

            - module(str)       : module type name in dotted format.

            - arguments(obj)    : Arguments object

        Properties:

            - instance(str)     : module instance name.

            - module(str)       : module type name in dotted format.

            - arguments(obj)    : Arguments object

            - category(str)     : The module type category.

            - group(str)        : The module type group.

            - name(str)         : The module type name.
        '''

        self.instance = instance
        self.module = module
        self.arguments = Arguments(**arguments)
        (self.category, self.group, self.name) = module.split('.')

    def __repr__(self):
        return "Module(%s)" % (self.module)


class Route(namedtuple('Route', 'source_module source_queue destination_module destination_queue'), object):
    pass


class ConfigManager(namedtuple('ConfigManager', 'modules routes')):
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

        modules = []
        for (name, module, arguments) in self.source.listModules():

            # find and replace lookup definitions
            args_incl_lookups = self.replaceLookupDefsWithFunctions(arguments)

            modules.append(Module(name, module, args_incl_lookups))

        routes = []
        for (sm, sq, dm, dq) in self.source.listRoutes():
            routes.append(Route(sm, sq, dm, dq))

        class Modules(namedtuple('Modules', ' '.join([x.instance for x in modules]))):
            pass

        class Routes(set):
            pass

        return ConfigManager(Modules(*modules), Routes(routes))

    def initializeLookupModules(self):

        for (name, module, arguments) in self.source.listLookups():
            m = importlib.import_module(module)
            self.lookup_methods[name] = m.Config(**arguments)

        m = importlib.import_module("wishbone.lookup.event")
        self.lookup_methods["event"] = m.Config()

    def replaceLookupDefsWithFunctions(self, args):

        for arg in args:
            if isinstance(args[arg], str) and args[arg].startswith('~'):
                (t, lookup, var) = self.extractLookupDef(args[arg])
                try:
                    if t == 'dynamic':
                        args[arg] = Lookup(self.lookup_methods[lookup].generateLookup(var))
                    else:
                        args[arg] = self.lookup_methods[lookup].generateLookup(var)()
                except KeyError:
                    raise ModuleInitFailure('"%s" is an unknown lookup instance name.' % (lookup))

        return args

    def extractLookupDef(self, e):

        m = re.match('(~*)(.*?)\([\"|\'](.*)?[\"|\']\)', e)
        if m is None:
            raise Exception("Invalid lookup definition: %s." % (e))
        if m.groups()[0] == '~':
            t = 'static'
        elif m.groups()[0] == '~~':
            t = 'dynamic'

        return (t, m.groups()[1], m.groups()[2])
