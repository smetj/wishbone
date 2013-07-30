#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  bootstrap.py
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

import argparse

class Start():

    def __init__(self, command, config, instances, loglevel, pid):
        pass

class Debug():

    def __init__(self, command, config, instances, loglevel, pid):
        pass

class Stop():

    def __init__(self, command, pid):
        pass

class Kill():

    def __init__(self, command, pid):
        pass

class List():

    def __init__(self, command, group ):
        pass

class Dispatch():

    def __init__(self):
        pass

    def start(self, command, config, instances, loglevel, pid):
        print command

    def debug(self, command, config, instances, loglevel, pid):
        print command

    def stop(self, command, pid):
        print command

    def kill(self, command, pid):
        print command

    def list(self, command, group):
        print command

def main():
    parser = argparse.ArgumentParser(description='Wishbone bootstrap server.')
    subparsers = parser.add_subparsers(dest='command')

    start = subparsers.add_parser('start', description="Starts a Wishbone instance and detaches to the background.  Logs are written to syslog.")
    start.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
    start.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
    start.add_argument('--loglevel', type=str, dest='loglevel', choices=['info','warn','crit','debug'], default='info', help='The maximum loglevel to show.')
    start.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

    debug = subparsers.add_parser('debug', description="Starts a Wishbone instance in foreground and writes logs to STDOUT.")
    debug.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
    debug.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
    debug.add_argument('--loglevel', type=str, dest='loglevel', choices=['info','warn','crit','debug'], default='info', help='The maximum loglevel to show.')
    debug.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

    stop = subparsers.add_parser('stop', description="Tries to gracefully stop the Wishbone instance.")
    stop.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

    kill = subparsers.add_parser('kill', description="Kills the Wishbone processes immediately.")
    kill.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

    llist = subparsers.add_parser('list', description="Lists the available Wishbone modules.")
    llist.add_argument('--group', type=str, dest='group', default='all', help='List the modules of this group type.')

    arguments=vars(parser.parse_args())

    dispatch=Dispatch()
    getattr(dispatch, arguments["command"])(**arguments)

if __name__ == '__main__':
    main()