#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configure_logging.py
#
#  Copyright 2013 Jelle Smet development@smetj.net
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

import logging
import sys
import os
import resource

class LogFilter(logging.Filter):
    '''Logging() Filter wich only allows Wishbone related logging.'''

    black_list_names = [ 'pyes', 'requests.packages.urllib3.connectionpool' ]

    def filter(self, record):
        if record.name in self.black_list_names:
            return False

        return True

class BOMLessFormatter(logging.Formatter):
    #http://serverfault.com/questions/407643/rsyslog-update-on-amazon-linux-suddenly-treats-info-level-messages-as-emerg
    def format(self, record):
        return logging.Formatter.format(self, record).encode('utf-8')
        
class ConfigureLogging():

    def initRootLogger(self, name='', syslog=False, loglevel=logging.INFO):

        if syslog == False:
            format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
            self.logging = logging.getLogger()
            self.logging.setLevel(loglevel)
            self.stream = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(format)
            self.stream.setFormatter(formatter)
            self.stream.addFilter(LogFilter())
            self.logging.addHandler(self.stream)
        else:
            format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
            from logging.handlers import SysLogHandler
            self.logging = logging.getLogger()
            self.logging.setLevel(loglevel)
            stream = SysLogHandler(address='/dev/log')
            
            formatter = BOMLessFormatter(format)
            stream.setFormatter(formatter)
            stream.addFilter(LogFilter())
            self.logging.addHandler(stream)

