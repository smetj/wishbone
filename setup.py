#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
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

from distutils.core import setup


if __name__ == '__main__':
    setup(name='wishbone',
        version='0.1',
        description='A python module which facilitates writing modular message passing code based on gevent.',
        author='Jelle Smet',
        author_email='development@smetj.net',
        url='https://github.com/smetj/wishbone',
	py_modules = [ "wishbone.main", "wishbone.server", "wishbone.toolkit", "wishbone.tools.configurelogging", "wishbone.tools.estools", "wishbone.tools.mongotools", "wishbone.io_modules.broker", "wishbone.io_modules.udpserver", "wishbone.io_modules.namedpipe", "wishbone.io_modules.socketfile", "wishbone.modules.skeleton", "wishbone.modules.jsonvalidator", "wishbone.modules.compressor", "wishbone.modules.stdout", "wishbone.modules.nagiosspoolwriter" ] )
