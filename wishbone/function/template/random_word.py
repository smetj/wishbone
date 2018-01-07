#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  random_word.py
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

from wishbone.function.template import TemplateFunction
import os
from random import choice
import io


class RandomWord(TemplateFunction):

    '''
    Returns a random word.

    A Wishbone template function which returns a randomly selected word from a
    word list.

    Args:

        filename (str): When None, a built-in word list is used otherwise the
                        referenced file is loaded.
        encoding (str): The encoding used to read the file.
    '''

    def __init__(self, filename=None, encoding="latin-1"):

        if filename is None:
            self.filename = "%s/../../data/wordlist.txt" % (os.path.dirname(__file__))
        else:
            self.filename = filename

        self.wordlist = self.readWordlist(filename, encoding)

    def readWordlist(self, location, encoding):
        with io.open(self.filename, encoding=encoding) as f:
            return f.readlines()

    def get(self):
        '''
        The function mapped to the template function.

        Args:
            None

        Returns:
            str: A random word
        '''

        return choice(self.wordlist).rstrip()
