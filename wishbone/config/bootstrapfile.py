#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bootstrapfile.py
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

import yaml


class Config(object):

    def __init__(self, filename):

        self.filename = filename
        self.__config = None

        self.__load()
        self.__verify()

    def listLookups(self):

        if "lookups" in self.__config:
            for lookup in self.__config["lookups"]:
                yield lookup, self.__config["lookups"][lookup]["module"], self.__config["lookups"][lookup].get("arguments", {})

    def listModules(self):
        for module in self.__config["modules"]:
            yield module, self.__config["modules"][module]["module"], self.__config["modules"][module].get("arguments", {})

    def listRoutes(self):
        for route in self.__config["routingtable"]:
            a, b, c, d = self.__splitRoute(route)
            yield a, b, c, d

    def __splitRoute(self, route):

        (source, destination) = route.split('->')
        (source_module, source_queue) = source.rstrip().lstrip().split('.')
        (destination_module, destination_queue) = destination.rstrip().lstrip().split('.')
        return source_module, source_queue, destination_module, destination_queue

    def __load(self):
        '''Loads and returns the yaml bootstrap file.'''

        try:
            with open(self.filename, 'r') as f:
                self.__config = yaml.load(f)
        except Exception as err:
            raise Exception("Failed to load bootstrap file.  Reason: %s" % (err))

    def __verify(self):
        assert "routingtable" in self.__config, "'routingtable' section not found in bootstrap file."
        assert "modules" in self.__config, "'modules' section not found in bootstrap file."
        for module in self.__config["modules"]:
            assert "module" in self.__config["modules"][module], "Cannot find the 'module' keyword in the '%s' module definition." % (module)
        # assert any([False for m in self.__config.keys() if m not in ["routingtable","modules"]]), "Unknown self.__config in bootstrap file."

        for route in self.__config["routingtable"]:
            (left, right) = route.split("->")
            assert "." in left.lstrip().rstrip(), "routingtable rule \"%s\" does not have the right format. Missing a dot." % (route)
            assert "." in right.lstrip().rstrip(), "routingtable rule \"%s\" does not have the right format. Missing a dot." % (route)

