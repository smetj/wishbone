#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configfile.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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
                        "description": {
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

    def __init__(self, filename, logstyle):
        self.logstyle = logstyle
        self.config = {"lookups": {}, "modules": {}, "routingtable": []}
        self.__addLogFunnel()
        self.__addMetricFunnel()
        self.load(filename)

    def addModule(self, name, module, arguments={}, description=""):

        if name.startswith('@'):
            raise Exception("Module instance names cannot start with @.")

        if name not in self.config["modules"]:
            self.config["modules"][name] = {'description': description, 'module': module, 'arguments': arguments}
            self.addConnection(name, "logs", "@logs", name)
            self.addConnection(name, "metrics", "@metrics", name)

        else:
            raise Exception("Module instance name '%s' is already taken." % (name))

    def addLookup(self, name, module, arguments={}):

        if name not in self.config["lookups"]:
            self.config["lookups"][name] = {"module": module, "arguments": arguments}
        else:
            raise Exception("Uplook instance name '%s' is already taken." % (name))

    def addConnection(self, source_module, source_queue, destination_module, destination_queue):

        if not self.__queueConnected(source_module, source_queue):
            self.config["routingtable"].append(AttrDict({"source_module": source_module, "source_queue": source_queue, "destination_module": destination_module, "destination_queue": destination_queue}))

    def dump(self):
        return AttrDict(self.config)

    def load(self, filename):

        config = self.__load(filename)
        self.__validate(config)
        self.__validateRoutingTable(config)

        if "lookups" in config:
            for lookup in config["lookups"]:
                self.addLookup(name=lookup, **config["lookups"][lookup])

        for module in config["modules"]:
            self.addModule(name=module, **config["modules"][module])

        for route in config["routingtable"]:
            sm, sq, dm, dq = self.__splitRoute(route)
            self.addConnection(sm, sq, dm, dq)

        getattr(self, "_setupLogging%s" % (self.logstyle.upper()))()

    def __queueConnected(self, module, queue):

        for c in self.config["routingtable"]:
            if (c["source_module"] == module and c["source_queue"] == queue) or (c["destination_module"] == module and c["destination_queue"] == queue):
                return True
        return False

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

    def __addLogFunnel(self):

        self.config["modules"]["@logs"] = {'description': "Centralizes the logs of all modules.", 'module': "wishbone.flow.funnel", "arguments": {}}

    def __addMetricFunnel(self):

        self.config["modules"]["@metrics"] = {'description': "Centralizes the metrics of all modules.", 'module': "wishbone.flow.funnel", "arguments": {}}

    def _setupLoggingSTDOUT(self):

        if not self.__queueConnected("@logs", "outbox"):
            self.config["modules"]["@logs_format"] = {'description': "Create a human readable log format.", 'module': "wishbone.encode.humanlogformat", "arguments": {}}
            self.addConnection("@logs", "outbox", "@logs_format", "inbox")
            self.config["modules"]["@logs_stdout"] = {'description': "Prints all incoming logs to STDOUT.", 'module': "wishbone.output.stdout", "arguments": {}}
            self.addConnection("@logs_format", "outbox", "@logs_stdout", "inbox")

    def _setupLoggingSYSLOG(self):

        if not self.__queueConnected("@logs", "outbox"):
            self.config["modules"]["@logs_syslog"] = {'description': "Writes all incoming messags to syslog.", 'module': "wishbone.output.syslog", "arguments": {}}
            self.addConnection("@logs", "outbox", "@logs_syslog", "inbox")

