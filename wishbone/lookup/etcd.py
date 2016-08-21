#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  etcd.py
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

from wishbone.lookup import Lookup
import requests
from uplook.errors import NoSuchValue


class ETCD(Lookup):

    '''
    **Returns a value from etcd.**

    Returns a value from an etcd instance.

    - Parameters to initialize the function:

        - base(str)("/v2/keys"): The base part of the endpoint.

    - Parameters to call the function:

        - key(str)(): The name of the key to request.
    '''

    def __init__(self, base="/v2/keys"):

        self.base = base.rstrip('/')

    def lookup(self, key):

        key = key.lstrip('/')

        try:
            response = requests.get('%s/%s' % (self.base, key))
            response.raise_for_status()
            return response.json()["node"]["value"]
        except Exception as err:
            raise NoSuchValue(str(err))
