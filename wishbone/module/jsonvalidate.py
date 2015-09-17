#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  jsonvalidate.py
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

from wishbone import Actor
from json import loads
from jsonschema import validate


class JSONValidate(Actor):

    '''**Validates JSON data against JSON-schema.**

    Validates the a Python dictionary (converted from a JSON string) against a
    predefined JSONschema. http://json-schema.org/

    The defined schema has to be valid JSON data.

    Events which do not pass validation are send to the default <failed> queue.

    Parameters:

        - schema(str)(None)
           |  The filename of the JSON validation schema to load.  When no
           |  schema is defined no validation is done.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config, schema=None):

        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):
        if self.kwargs.schema is not None:
            self.logging.debug("Validation schema defined.  Doing validation.")
            self.schema_data = self.__loadValidationSchema(self.kwargs.schema)
            self.validate = self.__validate
        else:
            self.logging.debug("No validation schema defined.  No validation.")
            self.validate = self.__noValidate

    def consume(self, event):

        try:
            self.validate(event.data)
        except Exception as err:
            self.logging.warn("JSON data does not pass the validation schema.  Reason: %s" % (
                str(err).replace("\n", " > ")))
            raise
        else:
            self.submit(event, self.pool.queue.outbox)

    def __loadValidationSchema(self, path):
        with open(path, 'r') as schema:
            data = ''.join(schema.readlines())
            return loads(data)

    def __validate(self, data):

        return validate(data, self.schema_data)

    def __noValidate(self, data):
        return True