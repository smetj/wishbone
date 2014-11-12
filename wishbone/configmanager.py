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


import importlib
import re


class Container(object):

    def list(self):
        for item in self.__dict__:
            yield item


class ListContainer(list):
    pass


class Arguments(object):

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
        self.arguments.__dict__.update(arguments)


class Route(object):

    def __init__(self, source_module, source_queue, destination_module, destination_queue):

        self.source = Source()
        self.source.module = source_module
        self.source.queue = source_queue

        self.destination = Destination()
        self.destination.module = destination_module
        self.destination.queue = destination_queue


class Config(object):

    def __init__(self, source):

        self.source = source
        self.modules = Container()
        self.routes = ListContainer()
        self.lookups = Container()
        self.__buildModules()
        self.__buildRoutes()
        self.__buildLookups()

    def __buildModules(self):

        for (name, module, arguments) in self.source.listModules():
            setattr(self.modules, name, Module(name, module, arguments))

    def __buildRoutes(self):

        for source_module, source_queue, destination_module, destination_queue in self.source.listRoutes():
            self.routes.append(Route(source_module, source_queue, destination_module, destination_queue))

    def __buildLookups(self):

        for (name, module, arguments) in self.source.listLookups():
            m = importlib.import_module(module)
            setattr(self.lookups, name, m.Config(**arguments))

        for m in self.listModules():
            for argument in m.arguments.list():
                if isinstance(m.arguments.get(argument), str) and m.arguments.get(argument).startswith("~"):
                    technique, var = self.__extractLookupDef(m.arguments.get(argument))

    def listModules(self):

        for m in self.modules.__dict__:
            yield self.modules.__dict__[m]

    def listRoutes(self):
        pass

    def __extractLookupDef(self, e):

        m = re.match('~(.*?)\([\"|\'](.*)?[\"|\']\)', e)
        return (m.groups()[0], m.groups()[1])


class ConfigurationFactory(object):

    @staticmethod
    def factory(name, *args, **kwargs):
        m = importlib.import_module(name)
        cfg = Config(m.Config(*args, **kwargs))
        return cfg
