#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configure_logging.py
#  
#  Copyright 2012 Jelle Smet development@smetj.net
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

class LogFilter(logging.Filter):
    '''Logging() Filter wich only allows Wishbone related logging.'''
    
    black_list_names = [ 'pyes', 'requests.packages.urllib3.connectionpool' ]
    
    def filter(self, record):
        if record.name in self.black_list_names:
            return False
        
        return True

    
def configureLogging(name=None, syslog=False, loglevel=logging.INFO, get_handle=False):
    '''Configures logging.
    
    Configures the format of the logging messages.  This function accepts 1 parameter:
    
    loglevel: defines the loglevel.'''
    
    if name == None:
        if syslog == False:
            format= '%(asctime)s %(levelname)s %(name)s: %(message)s'
        else:
            format= '%(levelname)s %(name)s: %(message)s'
    else:
        format= name+' %(name)s: %(message)s'
    if syslog == False:
        logger = logging.getLogger()
        logger.setLevel(loglevel)
        stream = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(format)
        stream.setFormatter(formatter)
        stream.addFilter(LogFilter())
        logger.addHandler(stream)
    else:
        from logging.handlers import SysLogHandler
        logger = logging.getLogger()
        logger.setLevel(loglevel)
        syslog = SysLogHandler(address='/dev/log')
        formatter = logging.Formatter(format)
        syslog.setFormatter(formatter)
        logger.addHandler(syslog)
        if get_handle == True:
            return syslog.socket.fileno()
