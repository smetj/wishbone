#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  event.py
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


class EventLookup(Lookup):

    '''
    **Returns the requested event header value.**

    - Parameters to initialize the function:

        None

    - Parameters to call the function:

        When calling the function a variable reference can be used similar to:

        ~~headerlookup("modulename.header.variablename","unknown")

        Keep in mind you always have to use a dynamic lookup function (double
        tilde).  You can provide a default value in case <variablename> does not
        exist in the header of namespace <modulename>.
    '''

    def __init__(self):
        pass

    def lookup(self):
        pass
