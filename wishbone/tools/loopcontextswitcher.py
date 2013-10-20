#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  loopcontextswitcher.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
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

from gevent import sleep

class LoopContextSwitcher():

    def __init__(self, loop_condition):
        self.loop_condition=loop_condition

    def get(self, iterations):

        class ContextSwitch():
            def __init__(self, iterations, loop_condition):
                self.iterations = iterations
                self.loop_condition = loop_condition
                self.__counter = 0

            def do(self):
                if self.__counter >= self.iterations:
                    self.__counter=0
                    #sleep(uniform(0.0001, 0.00001))
                    sleep()
                else:
                    self.__counter+=1

                return self.loop_condition

        return ContextSwitch(iterations, self.loop_condition).do


