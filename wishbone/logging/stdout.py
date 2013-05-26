#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  stdout.py
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
from time import strftime, localtime



class STDOUT(Actor):

    def __init__(self, name, debug=False):
        self.name=name
        self.debug=debug
        Actor.__init__(self, 'Logging')
        self.logging.info("Initiated")

    def consume(self, event):
        #('info', 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')
        if event["data"][0] == "debug" and self.debug == False:
            pass
        else:
            print ("%s %s %s %s: %s"%(
                strftime("%Y-%m-%dT%H:%M:%S", localtime(event["data"][1])),
                "Process",
                event["data"][2],
                event["data"][0],
                event["data"][3]))