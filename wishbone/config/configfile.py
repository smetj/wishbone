#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configfile.py
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
from wishbone.external.attrdict import AttrDict


class ConfigFile(object):

    def __init__(self):

        pass

    def load(self, filename):

        a = AttrDict(self.__processConfig(filename), recursive=True)
        if "lookups" not in a:
            a["lookups"] = {}
        return a

    def __processConfig(self, filename):

        config = self.__load(filename)
        if self.__verify(config):
            config["routingtable"] = self.__processRoutes(config["routingtable"])
        return config

    def __processRoutes(self, routes):

        r = []
        for route in routes:
            sm, sq, dm, dq = self.__splitRoute(route)
            r.append({"source_module": sm, "source_queue": sq, "destination_module": dm, "destination_queue": dq})
        return r

    def __splitRoute(self, route):

        (source, destination) = route.split('->')
        (source_module, source_queue) = source.rstrip().lstrip().split('.')
        (destination_module, destination_queue) = destination.rstrip().lstrip().split('.')
        return source_module, source_queue, destination_module, destination_queue

    def __load(self, filename):
        '''Loads and returns the yaml bootstrap file.'''

        try:
            with open(filename, 'r') as f:
                config = yaml.load(f)
        except Exception as err:
            raise Exception("Failed to load bootstrap file.  Reason: %s" % (err))
        else:
            return config

    def __verify(self, config):
        assert "routingtable" in config, "'routingtable' section not found in bootstrap file."
        assert "modules" in config, "'module' section not found in bootstrap file."
        for module in config["modules"]:
            assert "module" in config["modules"][module], "Cannot find the 'module' keyword in the '%s' module definition." % (module)

        for route in config["routingtable"]:
            (left, right) = route.split("->")
            assert "." in left.lstrip().rstrip(), "routingtable rule \"%s\" does not have the right format. Missing a dot." % (route)
            assert "." in right.lstrip().rstrip(), "routingtable rule \"%s\" does not have the right format. Missing a dot." % (route)

        return True

