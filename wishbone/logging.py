#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  logging.py
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


from wishbone.event import Event
from wishbone.error import QueueFull
from time import time
from os import getpid


class MockLogger():
    '''
    A wrapper around Logging which mimics logger.Logger
    '''

    def __init__(self, name, q, level=5):

        self.level = level
        self.l = Logging(name, q)

    def flush(self):
        pass

    def write(self, line):
        self.l._Logging__log(self.level, line.rstrip())

    def writelines(self, lines):
        for line in lines:
            self.l.Logging.__log(self.level, line.rstrip())


class Logging():

    '''
    Generates Wishbone formatted log messages following the Syslog priority
    definition.
    '''

    LEVELS = {
        0: "emergency",
        1: "alert",
        2: "critical",
        3: "error",
        4: "warning",
        5: "notice",
        6: "informational",
        7: "debug"
    }

    def __init__(self, name, q, identification=None):
        self.name = name
        self.logs = q
        self.identification = identification
        self.__queue_full_message = False
        self.__event_id = None

    def __log(self, level, message):

        event = Event({
            "time": time(),
            "identification": self.identification,
            "event_id": self.__event_id,
            "level": level,
            "txt_level": self.LEVELS[level],
            "pid": getpid(),
            "module": self.name,
            "message": message
        })

        try:
            self.logs.put(event)
        except QueueFull:
            if not self.__queue_full_message:
                print("Log queue full for module '%s'. Dropping messages" % (self.name))
            else:
                self.__queue_full_message = True

    def alert(self, message, *args, **kwargs):
        """Generates a log message with priority alert(1).
        """
        self.__log(1, message)

    def critical(self, message, *args, **kwargs):
        """Generates a log message with priority critical(2).
        """
        self.__log(2, message)
    crit = critical

    def debug(self, message, *args, **kwargs):
        """Generates a log message with priority debug(7).
        """
        self.__log(7, message)

    def emergency(self, message, *args, **kwargs):
        """Generates a log message with priority emergency(0).
        """
        self.__log(0, message)
    emerg = emergency
    exception = emergency

    def error(self, message, *args, **kwargs):
        """Generates a log message with priority error(3).
        """
        self.__log(3, message, *args, **kwargs)
    err = error

    def informational(self, message, *args, **kwargs):
        """Generates a log message with priority informational(6).
        """
        self.__log(6, message)
    info = informational

    def notice(self, message, *args, **kwargs):
        """Generates a log message with priority notice(5).
        """
        self.__log(5, message)

    def setCurrentEventID(self, event_id):

        self.__event_id = event_id

    def warning(self, message, *args, **kwargs):
        """Generates a log message with priority warning(4).
        """
        self.__log(4, message, *args, **kwargs)
    warn = warning
