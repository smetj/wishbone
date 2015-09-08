#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stdout.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
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

from wishbone import Actor
from os import getpid
from colorama import init, Fore, Back, Style


class Format():

    def __init__(self, complete, counter, pid):
        if complete:
            self.complete = self.__returnComplete
        else:
            self.complete = self.__returnIncomplete
        if counter:
            self.counter = self.__returnCounter
        else:
            self.counter = self.__returnNoCounter
        if pid:
            self.pid_value = getpid()
            self.pid = self.__returnPid
        else:
            self.pid = self.__returnNoPid

    def do(self, event):
        return self.pid(self.counter(self.complete(event)))

    def __returnComplete(self, event):
        return event.raw()

    def __returnIncomplete(self, event):
        return event.last.data

    def __returnCounter(self, event):
        self.countervalue += 1
        return "%s - %s" % (self.countervalue, event)

    def __returnNoCounter(self, event):
        return event

    def __returnNoPid(self, event):
        return event

    def __returnPid(self, event):
        return "PID-%s: %s" % (self.pid_value, event)


class STDOUT(Actor):

    '''**Prints incoming events to STDOUT.**

    Prints incoming events to STDOUT. When <complete> is True,
    the complete event including headers is printed to STDOUT.

    You can optionally define the colors used.


    Parameters:

        - complete(bool)(False)
           |  When True, print the complete event including headers.

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

        - color_ style(str)("NORMAL")
           |  The coloring style to use
           |  Valid values: DIM, NORMAL, BRIGHT


    Queues:

        - inbox
           |  Incoming events.
    '''

    def __init__(self, actor_config, complete=False, counter=False, prefix="", pid=False, foreground_color="WHITE", background_color="RESET", color_style="NORMAL"):
        Actor.__init__(self, actor_config)

        self.__validateInput(foreground_color, background_color, color_style)
        self.format = Format(self.kwargs.complete, self.kwargs.counter, self.kwargs.pid)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        init(autoreset=True)

    def consume(self, event):

        print("%s%s%s%s%s" % (getattr(Fore, self.kwargs.foreground_color),
                              getattr(Back, self.kwargs.background_color),
                              getattr(Style, self.kwargs.color_style),
                              self.kwargs.prefix, self.format.do(event)))

    def __validateInput(self, f, b, s):

        if f not in ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]:
            raise Exception("Foreground value is not correct.")
        if b not in ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "RESET"]:
            raise Exception("Background value is not correct.")
        if s not in ["DIM", "NORMAL", "BRIGHT"]:
            raise Exception("Style value is not correct.")
