#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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


class EventLookup():
    pass


def event():
    '''Returns the requested event header value.

    - Parameters to initialize the function:

        None

    - Parameters to call the function:

        When calling the function a variable reference can be used similar to:

        ~~headerlookup("modulename.header.variablename","unknown")

        Keep in mind you always have to use a dynamic lookup function (double
        tilde).  You can provide a default value in case <variablename> does not
        exist in the header of namespace <modulename>.
    '''

    return EventLookup()


def randomword(filename=None):
    '''Returns a random word.

    This function returns a random word from a wordlist.  Each line is a new
    word.

    - Parameters to initialize the function:

        - filename(str)(None): When value is None, a buildin wordlist is used.
                               If not a filename of a wordlist is expected.


    - Parameters to call the function:

        None
    '''

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

    return RandomWord(filename).pickWord


def randombool():
    '''Returns True or False.

    Returns True or False randomly.

    - Parameters to initialize the function:

        None

    - Parameters to call the function:

        None
    '''

    from random import getrandbits

    def randomBool():
        return bool(getrandbits(1))

    return randomBool


def randominteger(min=0, max=100):
    '''Returns a random integer.

    Returns a random integer between <min> and <max>.

    - Parameters to initialize the function:

        - min(int)(0): The minimum value
        - max(int)(0): The maximum value

    - Parameters to call the function:

        None
    '''
    from random import randint

    def randomInteger():
        return randint(min, max)

    return randomInteger
