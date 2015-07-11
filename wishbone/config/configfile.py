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
from jsonschema import validate

SCHEMA = {
    "type": "object",
    "properties": {
        "lookups": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string"
                        },
                        "arguments": {
                            "type": "object"
                        }
                    },
                    "required": ["module"],
                    "additionalProperties": False
                }
            }
        },
        "modules": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string"
                        },
                        "arguments": {
                            "type": "object"
                        }
                    },
                    "required": ["module"],
                    "additionalProperties": False
                }
            }
        },
        "routingtable": {
            "type": "array"
        }
    },
    "required": ["modules", "routingtable"],
    "additionalProperties": False
}


class ConfigFile(object):

    def __init__(self):

        pass

    def load(self, filename):

        config = self.__load(filename)
        self.__validate(config)
        self.__validateRoutingTable(config)

        if "lookups" not in config:
            config["lookups"] = {}

        config["routingtable"] = self.__processRoutes(config["routingtable"])

        config = AttrDict(config, recursive=True)

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

    def __validate(self, config):

        try:
            validate(config, SCHEMA)
        except Exception as err:
            raise Exception("Failed to validate configuration file.  Reason: %s" % (err.message))

    def __validateRoutingTable(self, config):

        for route in config["routingtable"]:
            (left, right) = route.split("->")
            assert "." in left.lstrip().rstrip(), "routingtable rule \"%s\" does not have the right format. Missing a dot." % (route)
            assert "." in right.lstrip().rstrip(), "routingtable rule \"%s\" does not have the right format. Missing a dot." % (route)