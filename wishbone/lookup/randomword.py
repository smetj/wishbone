#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  random_word.py
#
#  Copyright 2015 Jelle Smet <development@smetj.net>
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

from wishbone.error import ModuleInitFailure
import os
from random import choice


class RandomWord():

    def __init__(self, f=None):
        self.wordlist = self.readWordlist()

    def readWordlist(self):
        with open("%s/../data/wordlist.txt" % (os.path.dirname(__file__))) as f:
            return f.readlines()

    def pickWord(self):
        '''Returns a word as string from the wordlist.'''

        while True:
            word = choice(self.wordlist).rstrip()
            try:
                return word.encode("ascii", "ignore")
            except:
                pass