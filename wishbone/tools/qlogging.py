#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  qlogging.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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


from wishbone.tools import WishboneQueue
from time import time
from os import getpid

class QLogging():

    '''
    Generates Wishbone formatted log messages following the Syslog priority
    definition.

    Generated logs are stored in a local queue <self.logs>.  It is up to an
    external process the consume this queue.

    '''

    def __init__(self, name):
        self.logs=WishboneQueue()
        self.name=name
        self.pid=getpid()

    def __log(self, level, message):
        self.logs.put({"header":{},"data":(level, time(), self.pid, self.name, message)})

    def emergency(self, message):
        """Generates a log message with priority emergency(0).
        """
        self.__log(0, message)
    emerg=emergency

    def alert(self, message):
        """Generates a log message with priority alert(1).
        """
        self.__log(1, message)

    def critical(self, message):
        """Generates a log message with priority critical(2).
        """
        self.__log(2, message)
    crit=critical

    def error(self, message):
        """Generates a log message with priority error(3).
        """
        self.__log(3, message)
    err=error

    def warning(self, message):
        """Generates a log message with priority warning(4).
        """
        self.__log(4, message)
    warn=warning

    def notice(self, message):
        """Generates a log message with priority notice(5).
        """
        self.__log(5, message)

    def informational(self, message):
        """Generates a log message with priority informational(6).
        """
        self.__log(6, message)
    info=informational

    def debug(self, message):
        """Generates a log message with priority debug(7).
        """
        self.__log(7, message)