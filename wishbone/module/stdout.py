#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stdout.py
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

from gevent import monkey; monkey.patch_sys(stdin=False, stdout=True, stderr=False)
from wishbone.module import OutputModule
from os import getpid
from colorama import init, Fore, Back, Style
import sys
import re


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

    def __returnCounter(self, data):
        self.countervalue += 1
        return "%s - %s" % (self.countervalue, data)

    def __returnNoCounter(self, data):
        return data

    def __returnNoPid(self, data):
        return data

    def __returnPid(self, data):
        return "PID-%s: %s" % (self.pid_value, data)


class STDOUT(OutputModule):

    '''**Prints event data to STDOUT.**

    Prints incoming events to STDOUT. When <complete> is True,
    the complete event including headers is printed to STDOUT.

    You can optionally define the colors used.


    Parameters::

        - selection(str)(None)
           |  The event key to submit.
           |  If ``None`` the complete event is selected.

        - payload(str)(None)
           |  The string to submit.
           |  If defined takes precedence over `selection`.

        - native_event(bool)(False)
           |  If True, outgoing events are native events.

        - counter(bool)(False)
           |  Puts an incremental number for each event in front
           |  of each event.

        - prefix(str)("")*
           |  Puts the prefix in front of each printed event.

        - pid(bool)(False)
           |  Includes the pid of the process producing the output.

        - colorize(bool)(False)
           |  When True all STDOUT output is wrapped in between ANSI color
           |  escape sequences defined by `foreground_color`, `background_color`,
           |  `color_style`.

        - foreground_color(str)("WHITE")
           |  The foreground color.
           |  Valid values: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE

        - background_color(str)("RESET")
           |  The background color.
           |  Valid values: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

        - color_style(str)("NORMAL")
           |  The coloring style to use
           |  Valid values: DIM, NORMAL, BRIGHT

    Queues::

        - inbox
           |  Incoming events.
    '''

    def __init__(self, actor_config,
                 selection=None, payload=None, native_event=False,
                 counter=False, prefix="", pid=False, colorize=False,
                 foreground_color="WHITE", background_color="RESET", color_style="NORMAL"):
        OutputModule.__init__(self, actor_config)

        self.__validateInput(foreground_color, background_color, color_style)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        self.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def preHook(self):

        self.format = Format(
            self.kwargs.selection,
            self.kwargs.counter,
            self.kwargs.pid
        )

        if self.kwargs.colorize:
            init(autoreset=True)
            self.getString = self.__stringColor
        else:
            self.getString = self.__stringNoColor

    def consume(self, event):

        data = self.encode(
            self.getDataToSubmit(
                event
            )
        )

        output = self.getString(
            getattr(Fore, event.kwargs.foreground_color),
            getattr(Back, event.kwargs.background_color),
            getattr(Style, event.kwargs.color_style),
            event.kwargs.prefix,
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

    def __stringColor(self, f, b, s, p, d):
        return "%s%s%s%s%s\n" % (
            f,
            b,
            s,
            p,
            self.format.do(d)
        )

    def __stringNoColor(self, f, b, s, p, d):

        d = self.ansi_escape.sub('', str(d))

        return "%s%s\n" % (
            p,
            self.format.do(d)
        )
