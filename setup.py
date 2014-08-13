#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2014 Jelle Smet <development@smetj.net>
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

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

PROJECT = 'wishbone'
VERSION = '0.5.0'
install_requires = ['gevent>=1.0', 'argparse', 'greenlet>=0.3.2', 'jsonschema', 'prettytable', 'python-daemon', "pyyaml", "msgpack-python", "pyzmq", "amqp"]

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name=PROJECT,
    version=VERSION,

    description='A Python application framework and CLI tool to build and manage async event pipeline servers with minimal effort.',
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
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 ],
    extras_require={
        'testing': ['pytest'],
    },
    platforms=['Linux'],
    test_suite='wishbone.test.test_wishbone',
    cmdclass={'test': PyTest},
    scripts=[],

    provides=[],
    install_requires=install_requires,
    namespace_packages=[],
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': ['wishbone = wishbone.bootstrap:main'],
        'wishbone.flow': [
            'fanout = wishbone.module.fanout:Fanout',
            'funnel = wishbone.module.funnel:Funnel',
            'roundrobin = wishbone.module.roundrobin:RoundRobin'
        ],
        'wishbone.encode': [
            'graphite = wishbone.module.graphite:Graphite',
            'humanlogformat = wishbone.module.humanlogformat:HumanLogFormat',
            'msgpack = wishbone.module.msgpackencode:MSGPackEncode'
        ],
        'wishbone.decode': [
            'msgpack = wishbone.module.msgpackdecode:MSGPackDecode'
        ],
        'wishbone.function': [
            'header = wishbone.module.header:Header',
            # 'loglevelfilter = wishbone.module.loglevelfilter:LogLevelFilter'
        ],
        'wishbone.input': [
            'amqp = wishbone.module.amqpin:AMQPIn',
            'dictgenerator = wishbone.module.dictgenerator:DictGenerator',
            'disk = wishbone.module.diskin:DiskIn',
            'topic = wishbone.module.zmqtopicin:ZMQTopicIn',
            'tcp = wishbone.module.tcpin:TCPIn',
            'testevent = wishbone.module.testevent:TestEvent',
            'pull = wishbone.module.zmqpullin:ZMQPullIn'
        ],
        'wishbone.output': [
            'amqp = wishbone.module.amqpout:AMQPOut',
            'disk = wishbone.module.diskout:DiskOut',
            'null = wishbone.module.null:Null',
            'topic = wishbone.module.zmqtopicout:ZMQTopicOut',
            'stdout = wishbone.module.stdout:STDOUT',
            'syslog = wishbone.module.wbsyslog:Syslog',
            'tcp = wishbone.module.tcpout:TCPOut',
            'push = wishbone.module.zmqpushout:ZMQPushOut'
        ],
        'wishbone.contrib.flow': [
        ],
        'wishbone.contrib.encode': [
        ],
        'wishbone.contrib.decode': [
        ],
        'wishbone.contrib.function': [
        ],
        'wishbone.contrib.input': [
        ],
        'wishbone.contrib.output': [
        ]
    }
)
