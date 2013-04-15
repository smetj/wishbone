#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
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

PROJECT = 'wishbone'

VERSION = '0.3.2beta'


from setuptools import setup, find_packages

from distutils.util import convert_path
from fnmatch import fnmatchcase
import os
import sys

install_requires=['gevent>=1.0dev','python-daemon','egenix-mx-base','argparse','wb_log','greenlet>=0.3.2','jsonschema','prettytable']

try:
    import importlib
except ImportError:
    install_requires.append('importlib')

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='A Python library to write asynchronous event pipeline servers with minimal effort.',
    long_description=long_description,

    author='Jelle Smet',
    author_email='development@smetj.net',

    url='https://github.com/smetj/wishbone',
    download_url='https://github.com/smetj/wishbone/tarball/master',

    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Intended Audience :: Developers',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    dependency_links=['https://github.com/surfly/gevent/tarball/master#egg=gevent-1.0dev'],
    install_requires=install_requires,
    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
        'wishbone = wishbone.instance:main'
            ]
    },
)
