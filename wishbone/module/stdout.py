#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stdout.py
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
from gevent import monkey; monkey.patch_sys(stdin=False, stdout=True, stderr=False)
from wishbone import Actor
from os import getpid
from colorama import init, Fore, Back, Style
import sys
from wishbone.event import Bulk


class Format():

    def __init__(self, selection, counter, pid):
        self.selection = selection
        if counter:
            self.counter = self.__returnCounter
        else:
            self.counter = self.__returnNoCounter
        if pid:
            self.pid_value = getpid()
            self.pid = self.__returnPid
        else:
            self.pid = self.__returnNoPid

    def do(self, data):
        return self.pid(self.counter(data))

    # def __returnComplete(self, event):
    #     return event.raw(complete=True)

    # def __returnIncomplete(self, event):
    #     return event.get('@data')

    def __returnCounter(self, data):
        self.countervalue += 1
        return "%s - %s" % (self.countervalue, data)

    def __returnNoCounter(self, data):
        return data

    def __returnNoPid(self, data):
        return data

    def __returnPid(self, data):
        return "PID-%s: %s" % (self.pid_value, data)


class STDOUT(Actor):

    '''**Prints incoming events to STDOUT.**

    Prints incoming events to STDOUT. When <complete> is True,
    the complete event including headers is printed to STDOUT.

    You can optionally define the colors used.


    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - counter(bool)(False)
           |  Puts an incremental number for each event in front
           |  of each event.

        - prefix(str)("")*
           |  Puts the prefix in front of each printed event.

        - pid(bool)(False)
           |  Includes the pid of the process producing the output.

        - foreground_color(str)("WHITE")
           |  The foreground color.
           |  Valid values: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE

        - background_color(str)("RESET")
           |  The background color.
           |  Valid values: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

        - color_style(str)("NORMAL")
           |  The coloring style to use
           |  Valid values: DIM, NORMAL, BRIGHT

    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, actor_config, selection="@data", counter=False, prefix="", pid=False, foreground_color="WHITE", background_color="RESET", color_style="NORMAL"):
        Actor.__init__(self, actor_config)

        self.__validateInput(foreground_color, background_color, color_style)
        self.format = Format(self.kwargs.selection, self.kwargs.counter, self.kwargs.pid)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        init(autoreset=True)

    def consume(self, event):
        if isinstance(event, Bulk):
            data = event.dumpFieldAsList(self.kwargs.selection)
            data = "\n".join(data)
        else:
            data = event.get(self.kwargs.selection)

        output = "%s%s%s%s%s\n" % (
            getattr(Fore, self.kwargs.foreground_color),
            getattr(Back, self.kwargs.background_color),
            getattr(Style, self.kwargs.color_style),
            self.kwargs.prefix,
            self.format.do(data)
        )
        sys.stdout.write(output)
        sys.stdout.flush()

    def __validateInput(self, f, b, s):

        if f not in ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]:
            raise Exception("Foreground value is not correct.")
        if b not in ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "RESET"]:
            raise Exception("Background value is not correct.")
        if s not in ["DIM", "NORMAL", "BRIGHT"]:
            raise Exception("Style value is not correct.")
