#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  syslog.py
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

from wishbone import Actor
#from gevent import monkey;monkey.patch_all
import syslog
import sys
import os

class Syslog(Actor):
    '''**Writes Wishbone internal log formatted events to syslog.**

    (6, 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')

        Paramters:

            name(str)       :   The name of the module.


        Queues:

            inbox: incoming events
    '''

    def __init__(self, name):
        Actor.__init__(self, name, limit=0)
        self.name=name
        self.logging.info("Initiated")

    def preHook(self):
        syslog.openlog("%s(%s)"%(os.path.basename(sys.argv[0]), os.getpid()))

    def consume(self, event):
        syslog.syslog(event["data"][0], "%s: %s"%(event["data"][3], event["data"][4]))

    def postHook(self):
        syslog.closelog()
