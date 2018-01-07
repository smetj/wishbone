#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_utils.py
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

from wishbone.error import QueueEmpty
from gevent import sleep


def getter(queue):
    counter = 0
    while True:
        counter += 1
        if counter >= 5:
            raise Exception("No event from queue")
        else:
            try:
                return queue.get(block=False)
            except QueueEmpty:
                sleep(0.1)
