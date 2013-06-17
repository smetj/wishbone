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

    def __init__(self, name):
        self.logs=WishboneQueue()
        self.name=name
        self.pid=getpid()

    def __log(self, level, message):
        #print ((level, time(), self.name, message))
        self.logs.put({"header":{},"data":(level, time(), self.pid, self.name, message)})

    def debug(self, message):
        self.__log("debug",message)

    def warning(self, message):
        self.__log("warning",message)
    warn=warning

    def critical(self, message):
        self.__log("critical",message)
    crit=critical

    def info(self, message):
        self.__log("info",message)