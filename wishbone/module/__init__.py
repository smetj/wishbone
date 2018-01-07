#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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


from wishbone.actor import Actor
from wishbone.moduletype import ModuleType
from wishbone.componentmanager import ComponentManager
from wishbone.error import ModuleInitFailure


class InputModule(Actor):
    MODULE_TYPE = ModuleType.INPUT

    def setDecoder(self, name, *args, **kwargs):
        '''Sets a decoder.

        Args:
            name (str): The name of the decoder to initialize
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        '''
        self.decode = ComponentManager().getComponentByName(name)(*args, **kwargs).handler

    def decode(self, data):
        '''
        Decodes data into the desired format.

        This method gets replaced by a
        ::py:func:`wishbone.protocol.Decode.handler` method.

        Args:
            data (anything?): The data to decode.

        Returns:
            The decoded data
        '''

        raise ModuleInitFailure("No decoder set.")


class OutputModule(Actor):
    MODULE_TYPE = ModuleType.OUTPUT

    def setEncoder(self, name, *args, **kwargs):

        self.encode = ComponentManager().getComponentByName(name)(*args, **kwargs).handler

    def encode(self, data):
        '''
        Encodes data into the desired format.

        This method gets replaced by a
        ::py:func:`wishbone.protocol.Encode.handler` method.

        Args:
            data (anything?): The data to encode.

        Returns:
            The encoded data
        '''

        raise ModuleInitFailure("No encoder set.")


class FlowModule(Actor):
    MODULE_TYPE = ModuleType.FLOW


class ProcessModule(Actor):
    MODULE_TYPE = ModuleType.PROCESS
