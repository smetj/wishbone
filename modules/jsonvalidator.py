#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       jsonvalidator.py
#       
#       Copyright 2012 Jelle Smet development@smetj.net
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       #       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
#       

import json
from jsonschema import Validator
from wishbone.wishbone import PrimitiveActor

class JSONValidator(PrimitiveActor):
    
    def __init__(self, name, block, *args, **kwargs):
        PrimitiveActor.__init__(self, name, block)
        self.schema = kwargs.get('schema',None)
        self.loadSchema()

    def loadSchema(self):
        file = open(self.schema,'r')
        data = file.readlines()
        file.close()
        self.schema=json.loads(''.join(data))

    def consume(self, message):
        try:
            data = json.loads(message)
            self.validateBroker(data)
            self.outbox.put(data)
        except Exception as err:
            self.logging.warning('Invalid data received and purged. Reason: %s' % (err))

    def validateBroker(self,data):
        checker = Validator()
        checker.validate(data,self.schema)

    def shutdown(self):
        self.logging.info('Shutdown')
