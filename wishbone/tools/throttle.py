#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  throttle.py
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

from gevent import sleep


class SleepThrottle():

    def __init__(self):
        self.__throttle_sleep = 0.001
        self.throttle = self.__noThrottle
        self.throttle_state=False

    def enableThrottling(self):
        if self.throttle_state == False:
            self.throttle = self.__doThrottle
            self.throttle_state=True
            self.logging.info("Sleep throttling enabled.")

    def disableThrottling(self):
        if self.throttle_state == True:
            self.throttle = self.__noThrottle
            self.throttle_state=False
            self.logging.info("Sleep throttling disabled.")

    def __doThrottle(self):
        sleep(self.__throttle_sleep)

    def __noThrottle(self):
        pass