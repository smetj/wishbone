#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
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

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys, os

# Required to make pycrypto compile with PyPy
# https://github.com/dlitz/pycrypto/pull/59
if "PyPy" in sys.version:
    print("We are running PyPY, disable gmp to prevent pycrypto build error.")
    os.environ["with_gmp"] = "no"

PROJECT = 'wishbone'
VERSION = '1.1.0'

install_requires = ['gevent==1.1b4',
                    'greenlet==0.4.9',
                    'argparse==1.3.0',
                    'prettytable==0.7.2',
                    'python-daemon==1.6',
                    'pyyaml==3.11',
                    'msgpack-python==0.4.6',
                    'pyzmq==14.7.0',
                    'amqp==1.4.6',
                    'jinja2==2.8',
                    'jsonschema==2.5.1',
                    'gearman==2.0.2',
                    'pycrypto==2.6.1',
                    'flask==0.10.1',
                    'gevent_inotifyx==0.1.1',
                    'requests==2.7.0',
                    'colorama==0.3.3',
                    'arrow==0.6.0',
                    'elasticsearch==1.6.0',
                    'importlib==1.0.3',
                    'uplook==0.2']

# Deps pulled in by other modules
# 'lockfile==0.10.2'
# 'MarkupSafe==0.23'
# 'repoze.lru==0.6',
# 'werkzeug==0.10.4',
# 'itsdangerous==0.24',
# 'inotifyx==0.2.2',
# 'six==1.9.0',
# 'python-dateutil==2.4.2',
# 'urllib3==1.12',

try:
    with open('README.rst', 'rt') as f:
        long_description = f.read()
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

    description='Build event pipeline servers with minimal effort.',
    long_description=long_description,

    author='Jelle Smet',
    author_email='development@smetj.net',

    url='https://github.com/smetj/wishbone',
    download_url='https://github.com/smetj/wishbone/tarball/master',

    classifiers=['Development Status :: 5 - Production/Stable',
                 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 ],
    extras_require={
        'testing': ['pytest'],
    },
    platforms=['Linux'],
    test_suite='tests.test_wishbone',
    cmdclass={'test': PyTest},
    scripts=[],
    provides=[],
    install_requires=install_requires,
    namespace_packages=[],
    packages=find_packages(),
    package_data={'': ['data/wordlist.txt', 'data/LICENCE', 'data/sse.html', 'data/banner.tmpl']},
    zip_safe=False,
    entry_points={
        'console_scripts': ['wishbone = wishbone.bootstrap:main'],
        'wishbone.flow': [
            'fanout = wishbone.module.fanout:Fanout',
            'funnel = wishbone.module.funnel:Funnel',
            'match = wishbone.module.match:Match',
            'roundrobin = wishbone.module.roundrobin:RoundRobin',
            'consensus = wishbone.module.consensus:Consensus'
        ],
        'wishbone.encode': [
            'graphite = wishbone.module.graphite:Graphite',
            'humanlogformat = wishbone.module.humanlogformat:HumanLogFormat',
            'influxdb = wishbone.module.influxdb:InfluxDB',
            'msgpack = wishbone.module.msgpackencode:MSGPackEncode',
            'json = wishbone.module.jsonencode:JSONEncode'
        ],
        'wishbone.decode': [
            'msgpack = wishbone.module.msgpackdecode:MSGPackDecode',
            'json = wishbone.module.jsondecode:JSONDecode'
        ],
        'wishbone.function': [
            'header = wishbone.module.header:Header',
            'jsonvalidate = wishbone.module.jsonvalidate:JSONValidate',
            'keyvalue = wishbone.module.keyvalue:KeyValue',
            'loglevelfilter = wishbone.module.loglevelfilter:LogLevelFilter',
            'template = wishbone.module.template:Template'
        ],
        'wishbone.input': [
            'amqp = wishbone.module.amqpin:AMQPIn',
            'dictgenerator = wishbone.module.dictgenerator:DictGenerator',
            'disk = wishbone.module.diskin:DiskIn',
            'httpclient = wishbone.module.httpinclient:HTTPInClient',
            'httpserver = wishbone.module.httpinserver:HTTPInServer',
            'namedpipe = wishbone.module.namedpipein:NamedPipeIn',
            'pull = wishbone.module.zmqpullin:ZMQPullIn',
            'tcp = wishbone.module.tcpin:TCPIn',
            'testevent = wishbone.module.testevent:TestEvent',
            'topic = wishbone.module.zmqtopicin:ZMQTopicIn',
            'udp = wishbone.module.udpin:UDPIn',
            'gearman = wishbone.module.gearmanin:GearmanIn'
        ],
        'wishbone.output': [
            'amqp = wishbone.module.amqpout:AMQPOut',
            'disk = wishbone.module.diskout:DiskOut',
            'elasticsearch = wishbone.module.elasticsearchout:ElasticSearchOut',
            'email = wishbone.module.emailout:EmailOut',
            'file = wishbone.module.fileout:FileOut',
            'http = wishbone.module.httpoutclient:HTTPOutClient',
            'null = wishbone.module.null:Null',
            'topic = wishbone.module.zmqtopicout:ZMQTopicOut',
            'stdout = wishbone.module.stdout:STDOUT',
            'syslog = wishbone.module.wbsyslog:Syslog',
            'tcp = wishbone.module.tcpout:TCPOut',
            'push = wishbone.module.zmqpushout:ZMQPushOut',
            'udp = wishbone.module.udpout:UDPOut',
            'uds = wishbone.module.udsout:UDSOut',
            'sse = wishbone.module.sse:ServerSentEvents'
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
