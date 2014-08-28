#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  jsondecode.py
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

from wishbone import Actor
from json import loads
from jsonschema import Draft3Validator as Validator
from jsonschema import ValidationError


class JSONDecode(Actor):

    '''**Decodes and validates JSON events.**

    Decodes the payload or complete events from JSON format.
    Optionall valides the data structure against JSONschema.

    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - schema(str)(None)
           |  The filename of the JSON validation schema to load.  When no
           |  schema is defined no validation is done.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, name, size, frequency, schema=None):

        Actor.__init__(self, name)
        self.name = name
        self.schema = schema

        if schema is not None:
            self.logging.debug("Validation schema defined.  Doing validation.")
            schema_data = self.__loadValidationSchema(schema)
            self.validate = self.__validate
            self.validator = Validator(schema_data)
        else:
            self.logging.debug("No validation schema defined.  No validation.")
            self.validate = self.__noValidate

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        try:
            event["data"] = self.convert(event["data"])
        except Exception as err:
            self.logging.warn("Unable to convert incoming data.  Reason: %s" % (err))
            raise

        try:
            self.validate(event["data"])
        except ValidationError as err:
            self.logging.warn("JSON data does not pass the validation schema.  Purged.  Reason: %s" % (
                str(err).replace("\n", " > ")))
            raise

        self.submit(event, self.pool.queue.outbox)

    def __loadValidationSchema(self, path):
        with open(path, 'r') as schema:
            data = ''.join(schema.readlines())
            print loads(data)
            return loads(data)

    def convert(self, data):
        return loads(data)

    def __validate(self, data):
        return self.validator.validate(data)

    def __noValidate(self, data):
        return True