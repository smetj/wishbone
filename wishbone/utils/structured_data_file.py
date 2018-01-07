#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  structured_data_file.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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


import os
import json
import yaml
from gevent.lock import Semaphore
from jsonschema import validate
from wishbone.error import InvalidData


class StructuredDataFile():
    '''
    Loads and optionally validates structured data from disk.

    The module loads data from disk and optionally validates the data against
    the provided schema.  The datastructure can be JSON and/or YAML.

    Attributes:
        default (obj): The default value when no file content has loaded yet.
        schema (str): The JSONschema to validate the loaded data against.
        expect_json (bool): When True, the data structure can be JSON
        expect_yaml (bool): When True, the data structure can be YAML.
        expect_kv (bool): When True, the data structure can be Key/Value.
        content (dict): The loaded configurations.  Absolute paths are dict keys.
    '''

    def __init__(self, default=None, schema=None, expect_json=True, expect_yaml=True, expect_kv=True):
        '''
        Args:
            default (obj): A default value to return when no file content has loaded yet.
            schema (str): The JSONschema to validate the loaded data against.
            expect_json (bool): When True, the data structure can be JSON
            expect_yaml (bool): When True, the data structure can be YAML.
            expect_kv (bool): When True, the data structure can be Key/Value.
        '''

        self.default = default
        self.schema = schema
        self.expect_json = expect_json
        self.expect_yaml = expect_yaml
        self.expect_kv = expect_kv
        self.content = {}
        self.lock = Semaphore()

    def delete(self, path):
        '''Deletes the file content from the object'''

        abs_path = os.path.abspath(path)

        with self.lock:
            if abs_path in self.content.keys():
                del(self.content[abs_path])

    def dump(self):
        '''Dumps the complete cached content of all files
        If multiple files are cached then a list is returned.
        '''

        with self.lock:
            if self.content is {}:
                return self.default
            else:
                return self.content

    def dumpItems(self):
        '''
        Dumps the complete cached content file by file
        '''

        for filename, content in self.content.items():
            yield content

    def get(self, path):
        '''Returns the cached content of the file.  If the file isn't loaded yet, it
        tries to do that.'''

        abs_path = os.path.abspath(path)

        with self.lock:
            if abs_path not in self.content.keys():
                self.content[abs_path] = self.__load(abs_path)
            return self.content[abs_path]

    def load(self, path):
        '''Loads the file into the module and validates the content when required.'''

        abs_path = os.path.abspath(path)
        with self.lock:
            self.content[abs_path] = self.__load(abs_path)

    def __load(self, abs_path):

        if os.path.exists(abs_path) and os.access(abs_path, os.R_OK):
            if os.path.isfile(abs_path):
                content = self.__readFile(abs_path)
                if self.schema is not None:
                    try:
                        validate(content, self.schema)
                    except Exception as err:
                        raise InvalidData(err.message)
            else:
                raise Exception("'%s' does not appear to be a regular file." % (abs_path))
        else:
            raise Exception("File '%s' does not exist or is not accessible." % (abs_path))

        return content

    def __readFile(self, path):

        with open(path) as f:
            errors = []

            if self.expect_json:
                try:
                    f.seek(0)
                    return json.load(f)
                except Exception as err:
                    errors.append("JSON: %s" % str(err))
                else:
                    return

            if self.expect_yaml:
                try:
                    f.seek(0)
                    return yaml.load(f)
                except Exception as err:
                    errors.append("YAML: %s" % str(err))
                else:
                    return

            if self.expect_kv:
                try:
                    data = {}
                    f.seek(0)
                    for line in f.readlines():
                        splitted = line.split(":")
                        key = splitted[0]
                        value = ":".join(splitted[1:]).rstrip().lstrip()
                        data[key] = value
                    return data
                except Exception as err:
                    errors.append("KV: %s" % str(err))
                else:
                    return

            if len(errors) > 0:
                raise Exception("Could not load file '%s'.  Reason: '%s'" % (path, ",".join(errors)))
