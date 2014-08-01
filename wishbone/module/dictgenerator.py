#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       dictgenerator.py
#
#       Copyright 2014 Jelle Smet development@smetj.net
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

from random import choice, uniform, randint
from gevent import sleep, spawn
from wishbone import Actor
from wishbone.error import QueueFull
from wishbone.module import brit_a_z


class DictGenerator(Actor):

    '''**Generates random dictionaries.**

    This module allows you to generate an stream of dictionaries.

    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - randomize_keys(bool)(True)
           |  Randomizes the keys.  Otherwise keys are sequential
           |  numbers.

        - num_values(bool)(False)
           |  If true values will be numeric and randomized.

        - num_values_max(int)(1)
           |  The maximum of a value when they are numeric.

        - min_elements(int)(1)
           |  The minimum number of elements per dictionary.

        - max_elements(int)(1)
           |  The maximum number of elements per dictionary.

        - interval(int)(1)
           |  The time in seconds to sleep between each message.

    Queues:

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, name, size, frequency, randomize_keys=True, num_values=False, num_values_min=0, num_values_max=1, min_elements=1, max_elements=1, interval=1):
        Actor.__init__(self, name, size, frequency)
        self.pool.createQueue("outbox")
        self.name = name
        self.randomize_keys = randomize_keys
        self.num_values = num_values
        self.num_values_min = num_values_min
        self.num_values_max = num_values_max
        self.min_elements = min_elements
        self.max_elements = max_elements
        self.wordlist = brit_a_z.wordlist
        self.interval = interval
        self._total = 0

        self.key_number = -1

        if self.randomize_keys:
            self.generateKey = self.pickWord
        else:
            self.generateKey = self.generateKeyNumber

        if self.num_values:
            self.generateValue = self.generateValueNumber
        else:
            self.generateValue = self.pickWord

    def preHook(self):

        if self.interval > 0:
            self.sleep = self.__doSleep
        else:
            self.sleep = self.__doNoSleep

        spawn(self.generateDicts)

    def generateDicts(self):

        while self.loop():
            data = {}
            for x in xrange(0, randint(self.min_elements, self.max_elements)):
                data[self.generateKey()] = self.generateValue()
            self.sleep()
            self.submit({"header": {}, "data": data}, self.pool.queue.outbox)
            self.key_number = +1

    def pickWord(self):
        '''Returns a word as string from the wordlist.'''

        while self.loop():
            word = choice(self.wordlist).rstrip()
            try:
                return word.encode("ascii", "ignore")
            except:
                pass

    def generateValueInteger(self):
        '''Returns a random number.'''
        return randint(self.num_values_min, self.num_values_max)

    def generateKeyNumber(self):
        '''Generates a key by incrementing integer.'''
        self.key_number += 1
        return str(self.key_number)

    def __doSleep(self):
        sleep(self.interval)

    def __doNoSleep(self):
        pass
