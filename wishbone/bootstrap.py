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

from wishbone.router import Default
from pkg_resources import iter_entry_points
import argparse
import yaml
import sys


class Initialize():
    def __init__(self, command, filename, instances, loglevel, pid):
        self.command=command
        self.filename=filename
        self.instances=instances
        self.loglevel=loglevel
        self.pid=pid
        self.config=None
        self.router=Default(interval=1, rescue=False, uuid=False)

    def setup(self):
        self.config=self.loadConfig(self.filename)
        self.setupLogging()
        self.setupMetrics()
        self.setupModules()
        self.setupConnections()

    def setupMetrics(self):
        if "metrics" in self.config:
            for instance in self.config["metrics"]:
                module = self.loadModule(self.config["metrics"]["instance"]["module"])
                self.router.registerMetricModule((module, "metrics", 0), **self.config["metrics"][instance].get("arguments",{}))
        else:
            module = self.loadModule("wishbone.builtin.output.null")
            self.router.registerMetricModule((module, "metrics_null", 0))

    def setupModules(self):
        for instance in self.config["modules"]:
            module = self.loadModule(self.config["modules"][instance]["module"])
            self.router.register((module, instance, 0), **self.config["modules"][instance].get("arguments",{}))

    def setupConnections(self):
        for connection in self.config["routingtable"]:
            source=connection.split('->')[0].strip()
            destination=connection.split('->')[1].strip()
            self.router.connect(source, destination)

    def loadConfig(self, filename):
        try:
            with open (filename, 'r') as f:
                return yaml.load(f)
        except Exception as err:
            print "Failed to load config file.  Reason: %s"%(err)
            sys.exit(1)

    def loadModule(self, entrypoint):
        e=entrypoint.split('.')
        name=e[-1]
        del(e[-1])
        group=".".join(e)
        module_instance=None

        for module in iter_entry_points(group=group, name=name):
            try:
                module_instance=module.load()
            except Exception as err:
                print "Problem loading module %s  Reason: %s"%(module, err)
                sys.exit(1)

        if module_instance != None:
            return module_instance
        else:
            print "Failed to load module %s  Reason: Not found"%(entrypoint)
            sys.exit(1)

class Start(Initialize):
    pass

class Debug(Initialize):

    def setupLogging(self):
        if "logs" in self.config:
            for instance in self.config["logs"]:
                module = self.loadModule(self.config["logs"][instance]["module"])
                self.router.registerLogModule((module, "logformatfilter", 0), **self.config["logs"][instance].get("arguments",{}))
        else:
            loglevelfilter=self.loadModule("wishbone.builtin.logging.loglevelfilter")
            self.router.registerLogModule((loglevelfilter, "loglevelfilter", 0))

            stdout=self.loadModule("wishbone.builtin.output.stdout")
            self.router.register((stdout, "stdout", 0))

            self.router.connect("loglevelfilter.outbox", "stdout.inbox")

    def start(self):
        self.router.getChildren("loglevelfilter")
        self.router.start()
        self.router.block()

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
        start = Start(command, config, instances, loglevel, pid)
        start.do()

    def debug(self, command, config, instances, loglevel, pid):
        debug = Debug(command, config, instances, loglevel, pid)
        debug.setup()
        debug.start()

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