#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  queuepool.py
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

class QueuePool():

    def __init__(self):
        pass

    def shutdown(self):
        '''Closes all queues in preparation of actor shutdown.'''

        for q in self.__dict__.keys():
            self.__dict__[q].lock()

    def listQueues(self):
        '''return a list of available queues in the queuepool.'''

        return self.__dict__.keys()

    def messagesLeft(self):
        '''Checks each queue whether there are any messages left.'''
        qs=[]
        for q in self.__dict__.keys():
            if not self.__dict__[q].empty():
                qs.append(q)
        if len(qs) == 0:
            return []
        else:
            return qs

    def dump(self, name):
        '''Convenience function to self.<name>.dump'''
        return self.__dict__[name].dump()