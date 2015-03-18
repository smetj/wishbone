#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configurationfactory.py
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

from wishbone.error import ModuleInitFailure
from collections import namedtuple
from uplook import UpLook
import importlib
import re
import sys


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

        '''Module data type

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
        self.arguments = Arguments(**arguments.dump())
        (self.category, self.group, self.name) = module.split('.')

    def __repr__(self):
        return "Module(%s)" % (self.module)


class Route(namedtuple('Route', 'source_module source_queue destination_module destination_queue'), object):

    '''Route data type'''

    pass


class ConfigManager(namedtuple('ConfigManager', 'modules routes')):

    '''ConfigManager data type'''

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

            uplook = UpLook(**arguments)

            for f in uplook.listFunctions():
                uplook.registerLookup(f, self.lookup_methods[f])
            modules.append(Module(name, module, uplook))

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

            base = ".".join(module.split('.')[0:-1])
            function = module.split('.')[-1]
            m = importlib.import_module(base)
            self.lookup_methods[name] = getattr(m, function)(**arguments)

        self.lookup_methods["event"] = getattr(importlib.import_module("wishbone.lookup"), "event")()
