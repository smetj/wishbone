#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  actorconfig.py
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


class ActorConfig(object):

    '''
    A configuration object pass to a Wishbone actor.

    This is a simple object which holds a set of attributes (with some sane
    defaults) a Wishbone Actor expects.

    Attributes:
        name (str): The name identifying the actor instance.
        size (int): The size of the Actor instance's queues.
        frequency (int): The time in seconds to generate metrics.
        template_functions (dict): A dictionary of template functions.
        description (str): A short free form discription of the actor instance.
        module_functions (dict): A dict of queue names containing an array of module_functions
        protocol (``wishbone.protocol.Encode``, ``wishbone.protocol.Encode``): A protocol decode or encode instance.
        io_event (bool): When ``True`` Input and Output modules know to expect or emit serialzed wishbone events.
        identification (str): A name assigned to the Wishbone instance, useful for the module to know such as logging.
        disable_exception_handling (bool): If True, exception handling is disabled. Usefull for testing
    '''

    def __init__(self, name, size=100, frequency=10, template_functions={}, description=None, module_functions={},
                 protocol=None, io_event=False,
                 identification="wishbone",
                 disable_exception_handling=False):
        '''
        Args:
            name (str): The name identifying the actor instance.
            size (int): The size of the Actor instance's queues.
            frequency (int): The time in seconds to generate metrics.
            template_functions (dict): A dictionary of template functions.
            description (str): A short free form discription of the actor instance.
            module_functions (dict): A dict of queue names containing an array of module_functions.
            protocol (``wishbone.protocol.Encode``, ``wishbone.protocol.Encode``): A protocol decode or encode instance.
            io_event (bool): When ``True`` Input and Output modules know to expect or emit serialzed wishbone events.
            identification (str): A name assigned to the Wishbone instance, useful for the module to know such as logging.
            disable_exception_handling (bool): If True, exception handling is disabled. Usefull for testing
        '''
        self.name = name
        self.size = size
        self.frequency = frequency
        self.template_functions = template_functions
        self.description = description
        self.module_functions = module_functions
        self.protocol = protocol
        self.io_event = io_event
        self.identification = identification
        self.disable_exception_handling = disable_exception_handling
