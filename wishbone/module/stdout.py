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
#from gevent import monkey;monkey.patch_sys()
from os import getpid

class Format():

    def __init__(self, complete, counter, pid):
        self.countervalue=-1
        if complete == True:
            self.complete = self.__returnComplete
        else:
            self.complete = self.__returnIncomplete
        if counter == True:
            self.counter = self.__returnCounter
        else:
            self.counter = self.__returnNoCounter
        if pid == True:
            self.pid_value = getpid()
            self.pid = self.__returnPid
        else:
            self.pid = self.__returnNoPid

    def do(self, event):
        return self.pid(self.counter(self.complete(event)))

    def __returnComplete(self, event):
        return event

    def __returnIncomplete(self, event):
        return event["data"]

    def __returnCounter(self, event):
        self.countervalue += 1
        return "%s - %s"%(self.countervalue, event)

    def __returnNoCounter(self, event):
        return event

    def __returnNoPid(self, event):
        return event

    def __returnPid(self, event):
        return "PID-%s: %s"%(self.pid_value, event)

class STDOUT(Actor):
    '''**Prints incoming events to STDOUT.**

    Prints incoming events to STDOUT. When <complete> is True,
    the complete event including headers is printed to STDOUT.

    Parameters:

        - name (str):       The instance name when initiated.

        - complete (bool):  When True, print the complete event including headers.
                            Default: False

        - counter (bool):   Puts an incremental number for each event in front of each event.
                            Default: False

        - prefix (str):     Puts the prefix in front of each printed event.
                            Default: ""

        - pid (bool):       Includes the pid of the process producing the output.
                            Default: False

    Queues:

        - inbox:    Incoming events.
    '''

    def __init__(self, name, complete=False, counter=False, prefix="", pid=False):
        Actor.__init__(self, name)
        self.deleteQueue("outbox")
        self.complete=complete
        self.counter=counter
        self.prefix=prefix
        self.format=Format(complete, counter, pid)

    def consume(self,event):
        #todo(smet) This should work in a gevent context but it doesn't. Bug?
        #sys.stdout.write(self.format.do(event))
        print unicode(("%s%s"%(self.prefix,self.format.do(event))))