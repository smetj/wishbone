#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       stdout.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone import Actor
#from sys import stdout

class Format():

    def __init__(self, complete, counter):
        self.countervalue=-1
        if complete == True:
            self.complete = self.__returnComplete
        else:
            self.complete = self.__returnIncomplete
        if counter == True:
            self.counter = self.__returnCounter
        else:
            self.counter = self.__returnNoCounter

    def do(self, event):
        return self.counter(self.complete(event))

    def __returnComplete(self, event):
        return event

    def __returnIncomplete(self, event):
        return event["data"]

    def __returnCounter(self, event):
        self.countervalue += 1
        return "%s - %s"%(self.countervalue, event)

    def __returnNoCounter(self, event):
        return event

class STDOUT(Actor):
    '''**A builtin Wishbone module prints events to STDOUT.**

    Prints incoming events to STDOUT. When <complete> is True,
    the complete event including headers is printed to STDOUT.

    Parameters:

        - name (str):       The instance name when initiated.

        - complete (bool):  When True, print the complete event including headers.

        - counter (bool):   Puts an incremental number for each event in front of each event.

    Queues:

        - inbox:    Incoming events.
    '''

    def __init__(self, name, complete=False, counter=False):
        Actor.__init__(self, name, limit=0)
        self.queueDelete("outbox")
        self.complete=complete
        self.counter=counter
        self.format=Format(complete, counter)

    def consume(self,event):
        #todo(smetj): This module makes use of the print() function.
        #This should be changed into stdout.write() but that's not gevent friendly

        print self.format.do(event)