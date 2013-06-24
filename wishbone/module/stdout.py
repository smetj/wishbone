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
        self.counter=-1
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
        counter += 1
        return "%s - %s"%(self.counter, event)

    def __returnNoCounter(self, event):
        return event

class STDOUT(Actor):
    '''**A builtin Wishbone module prints events to STDOUT.**

    After printing the content of the events to STDOUT they are put into the outbox
    queue unless otherwise defined using the purge parameter.  When the complete
    parameter is True, the complete event is printed to STDOUT.

    Parameters:

        - name (str):       The instance name when initiated.
        - enable (bool):    When True, prints to STDOUT, when false not.
        - complete (bool):  When True, print the complete event including headers.
        - purge (bool):     When True the message is dropped and not put in outbox.
        - counter (bool):   Puts an incremental number for each event in front of each event.

    Queues:

        - inbox:    Incoming events.
        - outbox:   Outgoing events.
    '''

    def __init__(self, name, complete=False, purge=False, counter=False):
        Actor.__init__(self, name, limit=0)
        self.complete=complete
        self.purge=purge
        self.counter=counter
        self.format=Format(complete, counter)

    def consume(self,event):
        #todo(smetj): This module makes use of the print() function.
        #This should be changed into stdout.write() but that's not gevent friendly

        print self.format.do(event)
        if self.purge == False:
            self.queuepool.outbox(doc)

    def shutdown(self):
        self.logging.info('Shutdown')