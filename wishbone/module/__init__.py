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
from wishbone.event import extractBulkItemValues
from wishbone.protocol import Encode, Decode
from wishbone.event import Event as Wishbone_Event
from wishbone.protocol.decode.dummy import Dummy as DummyDecoder
from wishbone.protocol.encode.dummy import Dummy as DummyEncoder
from wishbone.error import TTLExpired
from copy import deepcopy
from sys import exc_info
import traceback
from gevent.pool import Pool


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

    decode = DummyDecoder().handler

    def _generateNativeEvent(self, data={}, destination=None):
        '''
        Gets mapps to self.generateEvent for `input` type modules and if
        ``Actor.config.protocol_event`` is ``True``.

        Args:
            data (dict): The dict representation of ``wishbone.event.Event``.
            destination (str): The destination str to store ``data``. In this
                               particular implementation it's ignored.

        Returns:
            wishbone.event.Event: ``Event`` instance of ``data``
        '''

        e = Wishbone_Event()
        e.slurp(data)
        return e

    def _moduleInitSetup(self):
        '''
        Does module type specific setup.
        '''

        if not hasattr(self, "decode") and self.config.protocol is None:
            self.logging.debug("This 'Input' module has no decoder method set. Setting dummy decoder.")
            self.setDecoder("wishbone.protocol.decode.dummy")
        if self.config.protocol is not None:
            self.logging.debug("This 'Input' module has '%s' decoder configured." % (self.config.protocol))
            self.decode = self.config.protocol.handler

        if self.kwargs.native_events:
            self.generateEvent = self._generateNativeEvent

    def _moduleInitValidation(self):
        '''
        Validates whether we have all the parameters this module type expects

        Args:
            None

        Returns:
            None

        Raises:
            ModuleInitFailure: Raised when one of the components isn't correct.
        '''

        if self.config.protocol is not None and not isinstance(self.config.protocol, Decode):
            raise ModuleInitFailure("An 'input' module should have a decode protocol set. Found %s" % (type(self.config.protocol)))

        for param in ["native_events", "destination"]:
            if param not in self.kwargs.keys():
                raise ModuleInitFailure("An 'Input' module should always have a '%s' parameter. This is a programming error." % (param))


class OutputModule(Actor):
    MODULE_TYPE = ModuleType.OUTPUT

    def setEncoder(self, name, *args, **kwargs):

        self.encode = ComponentManager().getComponentByName(name)(*args, **kwargs).handler

    encode = DummyEncoder().handler

    def getDataToSubmit(self, event):
        '''
        Derives the data to submit from ``event`` taking into account
        ``native_events``, ``payload`` and ``selection`` module parameters.

        Args:
            event (```wishbone.event.Event```): The event to extract data from.

        Returns:

            dict/str/...: The data to submit.
        '''

        if self.kwargs.native_events:
            return event.getNative()
        elif event.kwargs.payload is None:
            if event.isBulk():
                return "\n".join([str(item) for item in extractBulkItemValues(event, self.kwargs.selection)])
            else:
                return event.get(
                    event.kwargs.selection
                )
        else:
            return event.kwargs.payload

    def _consumer(self, function, queue):
        '''

        Greenthread which applies <function> to each element from <queue>.
        However, this version overrides ``Actor._consumer`` as it executes
        parallel coroutine versions of ``functions`` spawned on a
        ``gevent.pool.Pool`` instance.  The number of parallel instances is
        defined by the ``parallel_streams`` value.

        Args:
            function (``function``): The function which has been registered to consume ``queue``.

            queue (str): The name of the queue from which events have to be
                         consumed and processed by ``function``.

        Returns:
            None
        '''

        self.parallel_pool = Pool(self.kwargs.parallel_streams)
        self._run.wait()
        self.logging.debug("Function '%s' has been registered to consume queue '%s'" % (function.__name__, queue))

        def execFunction(function, event):
            try:
                function(deepcopy(event))
            except Exception as err:
                if self.config.disable_exception_handling:
                    raise
                exc_type, exc_value, exc_traceback = exc_info()
                info = (traceback.extract_tb(exc_traceback)[-1][1], str(exc_type), str(exc_value))

                event.set(info, "errors.%s" % (self.name))

                self.logging.error("%s" % (err))
                self.submit(event, "_failed")
            else:
                self.submit(event, "_success")
            finally:
                # Unset the current event uuid to the logger object
                self.logging.setCurrentEventID(None)

        while self.loop():

            event = self.pool.getQueue(queue).get()
            if not event.has("tmp.%s" % (self.name)):
                event.set({}, "tmp.%s" % (self.name))

            # Render kwargs relative to the event's content and make these accessible under event.kwargs
            event.renderKwargs(self.kwargs_template)

            # Validate TTL
            try:
                event.decrementTTL()
            except TTLExpired as err:
                self.logging.warning("Event with UUID %s dropped. Reason: %s" % (event.get("uuid"), err))
                continue

            # Set the current event uuid to the logger object
            self.logging.setCurrentEventID(event.get("uuid"))

            # Apply all the defined queue functions to the event
            event = self._applyFunctions(queue, event)

            # Apply consumer function
            self.parallel_pool.spawn(execFunction, function, event)

    def _moduleInitSetup(self):
        '''
        Does module type specific setup.
        '''

        if not hasattr(self, "encode") and self.config.protocol is None:
            self.logging.debug("This 'Output' module has no encoder method set. Setting dummy decoder.")
            self.setEncoder("wishbone.protocol.encode.dummy")
        if self.config.protocol is not None:
            self.logging.debug("This 'Output' module has '%s' encoder configured." % (self.config.protocol))
            self.encode = self.config.protocol.handler

    def _moduleInitValidation(self):
        '''
        Validates whether we have all the parameters this module type expects

        Args:
            None

        Returns:
            None

        Raises:
            ModuleInitFailure: Raised when one of the components isn't correct.
        '''

        if self.config.protocol is not None and not isinstance(self.config.protocol, Encode):
            raise ModuleInitFailure("An 'output' module should have a encode protocol set. Found %s" % (type(self.config.protocol)))

        for param in ["payload", "selection", "native_events", "parallel_streams"]:
            if param not in self.kwargs.keys():
                raise ModuleInitFailure("An 'output' module should always have a '%s' parameter. This is a programming error." % (param))


class FlowModule(Actor):
    MODULE_TYPE = ModuleType.FLOW

    def _moduleInitSetup(self):
        '''
        Does module type specific setup.
        '''

        pass

    def _moduleInitValidation(self):
        '''
        Validates whether we have all the parameters this module type expects

        Args:
            None

        Returns:
            None

        Raises:
            ModuleInitFailure: Raised when one of the components isn't correct.
        '''

        pass


class ProcessModule(Actor):
    MODULE_TYPE = ModuleType.PROCESS

    def _moduleInitSetup(self):
        '''
        Does module type specific setup.
        '''

        pass

    def _moduleInitValidation(self):
        '''
        Validates whether we have all the parameters this module type expects

        Args:
            None

        Returns:
            None

        Raises:
            ModuleInitFailure: Raised when one of the components isn't correct.
        '''

        pass
