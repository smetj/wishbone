#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bootstrap.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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

import gipc
import argparse
import os
import sys
# http://stackoverflow.com/questions/4554271/how-to-avoid-excessive-stat-etc-localtime-calls-in-strftime-on-linux
os.environ["TZ"] = ":/etc/localtime"

from wishbone.router import Default
from wishbone import ModuleManager
from wishbone.config import ConfigFile
from wishbone.utils import PIDFile
from gevent import signal
from gevent.event import Event
from daemon import DaemonContext
from pkg_resources import get_distribution
from setproctitle import setproctitle


class BootStrap():

    '''Parses command line arguments and bootstraps the Wishbone instance.
    '''

    def __init__(self, description="Wishbone bootstrap server. Build composable event pipeline servers with minimal effort.", include_groups=[]):

        parser = argparse.ArgumentParser(description=description)
        subparsers = parser.add_subparsers(dest='command')

        start = subparsers.add_parser('start', description="Starts a Wishbone instance and detaches to the background.  Logs are written to syslog.")
        start.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        start.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        start.add_argument('--pid', type=str, dest='pid', default='%s/wishbone.pid' % (os.getcwd()), help='The pidfile to use.')
        start.add_argument('--queue_size', type=int, dest='queue_size', default=100, help='The queue size to use.')
        start.add_argument('--frequency', type=int, dest='frequency', default=1, help='The metric frequency.')
        start.add_argument('--id', type=str, dest='identification', default=None, help='An identification string.')
        start.add_argument('--module_path', type=str, dest='module_path', default=None, help='A comma separated list of directories to search and find Wishbone modules.')

        debug = subparsers.add_parser('debug', description="Starts a Wishbone instance in foreground and writes logs to STDOUT.")
        debug.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        debug.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        debug.add_argument('--queue_size', type=int, dest='queue_size', default=100, help='The queue size to use.')
        debug.add_argument('--frequency', type=int, dest='frequency', default=1, help='The metric frequency.')
        debug.add_argument('--id', type=str, dest='identification', default=None, help='An identification string.')
        debug.add_argument('--module_path', type=str, dest='module_path', default=None, help='A comma separated list of directories to search and find Wishbone modules.')
        debug.add_argument('--graph', action="store_true", help='When enabled starts a webserver on 8088 showing a graph of connected modules and queues.')
        debug.add_argument('--graph_include_sys', action="store_true", help='When enabled includes logs and metrics related queues modules and queues to graph layout.')

        debug.add_argument('--profile', action="store_true", help='When enabled profiles the process and dumps a profile file in the current directory. The profile file can be loaded in Chrome developer tools.')

        stop = subparsers.add_parser('stop', description="Tries to gracefully stop the Wishbone instance.")
        stop.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        kill = subparsers.add_parser('kill', description="Kills the Wishbone processes immediately.")
        kill.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        subparsers.add_parser('list', description="Lists the available Wishbone modules and lookup.")

        show = subparsers.add_parser('show', description="Shows the details of a module.")
        show.add_argument('--module', type=str, required=True, help='Shows the documentation of the module. ')

        arguments = vars(parser.parse_args())

        dispatch = Dispatch(**arguments)
        getattr(dispatch, arguments["command"])()


class Dispatch():

    '''Handles the Wishbone commands, processes and daemons.
    '''

    def __init__(self, **kwargs):
        self.command = kwargs.get("command", None)
        self.config = kwargs.get("config", None)
        self.instances = kwargs.get("instances", None)
        self.pid = kwargs.get("pid", None)
        self.queue_size = kwargs.get("queue_size", None)
        self.frequency = kwargs.get("frequency", None)
        self.identification = kwargs.get("identification", None)
        self.module_path = kwargs.get("module_path", None)
        self.graph = kwargs.get("graph", None)
        self.graph_include_sys = kwargs.get("graph_include_sys", None)
        self.profile = kwargs.get("profile", None)
        self.module = kwargs.get("module", None)

        self.routers = []

        if self.module_path is not None:
            self.__expandSearchPath(self.module_path)

    def initializeRouter(self, config):
        '''Initializes a Router instance using the provided config object.

        This function blocks until signal(2) is received after which it
        continues and executes the router's stop() method.

        The idea is that you can spawn this function to the background to have
        multiple parallel instances.

        Args:
            config (Wishbone.config.configfile:ConfigFile): The router configuration
        '''

        def startRouter():
            if self.identification is not None:
                setproctitle(self.identification)

            router = Default(
                config,
                size=self.queue_size,
                frequency=self.frequency,
                identification=self.identification,
                graph=self.graph,
                graph_include_sys=self.graph_include_sys
            )

            router.start()
            e.wait()
            router.stop()

        e = Event()
        e.clear()
        signal(2, e.set)

        if self.profile:
            from wishbone.utils.py2devtools import Profiler
            with Profiler():
                startRouter()
        else:
            startRouter()

    def bootstrapBlock(self):
        '''Helper function which blocks untill all running routers have stopped.
        '''

        while True:
            try:
                for router in self.routers:
                    router.join()
                break
            except KeyboardInterrupt:
                pass

    def generateHeader(self):
        '''Generates the Wishbone ascii header.
        '''

        with open("%s/data/banner.tmpl" % (os.path.dirname(__file__))) as f:
            template = ''.join(f.readlines()).format(version=get_distribution('wishbone').version)

        return template

    def debug(self):
        '''Maps to the CLI command and starts Wishbone in foreground.
        '''

        router_config = ConfigFile(self.config, 'STDOUT').dump()

        if self.instances == 1:
            sys.stdout.write("\nInstance started in foreground with pid %s\n" % (os.getpid()))
            self.initializeRouter(router_config)

        else:
            for instance in range(self.instances):
                self.routers.append(
                    gipc.start_process(
                        self.initializeRouter,
                        args=(router_config, ),
                        daemon=True
                    )
                )

            pids = [str(p.pid) for p in self.routers]
            print(("\nInstances started in foreground with pid %s\n" % (", ".join(pids))))
            self.bootstrapBlock()

    def list(self):
        '''Maps to the CLI command and lists all Wishbone entrypoint modules it can find.
        '''

        categories = ["wishbone", "wishbone_contrib"]
        groups = ["flow", "encode", "decode", "function", "input", "output"]

        print((self.generateHeader()))
        print("Available event modules:")
        print((ModuleManager(categories=categories, groups=groups).getModuleTable()))
        print("\n")
        print("Available lookup function modules:")
        print((ModuleManager(categories=categories, groups=["lookup"]).getModuleTable()))

    def show(self):
        '''Maps to the CLI command and shows the docstring of the Wishbone module.
        '''

        module_manager = ModuleManager()
        module_manager.validateModuleName(self.module)
        module_manager.exists(self.module)

        print((self.generateHeader()))

        try:
            (category, group, self.module) = self.module.split('.')
        except ValueError:
            (category, sub, group, self.module) = self.module.split('.')
            category = "%s.%s" % (category, sub)

        try:
            title = module_manager.getModuleTitle(category, group, self.module)
            version = module_manager.getModuleVersion(category, group, self.module)
            header = "%s.%s.%s" % (category, group, self.module)
            print("")
            print(("="*len(header)))
            print(header)
            print(("="*len(header)))
            print("")
            print(("Version: %s" % (version)))
            print("")
            print(title)
            print(("-"*len(title)))
            print((module_manager.getModuleDoc(category, group, self.module)))
        except Exception as err:
            print(("Failed to load module %s.%s.%s. Reason: %s" % (category, group, self.module, err)))

    def start(self):
        '''Maps to the CLI command and starts one or more Wishbone processes in background.
        '''

        router_config = ConfigFile(self.config, 'SYSLOG').dump()
        pid_file = PIDFile(self.pid)

        with DaemonContext(stdout=sys.stdout, stderr=sys.stderr, detach_process=True):
            if self.instances == 1:
                sys.stdout.write("\nWishbone instance started with pid %s\n" % (os.getpid()))
                sys.stdout.flush()
                pid_file.create([os.getpid()])
                self.initializeRouter(router_config)
            else:
                for instance in range(self.instances):
                    self.routers.append(
                        gipc.start_process(
                            self.initializeRouter,
                            args=(router_config, ),
                            daemon=True
                        )
                    )

                pids = [str(p.pid) for p in self.routers]
                print(("\nInstances started in foreground with pid %s\n" % (", ".join(pids))))
                pid_file.create(pids)

            self.bootstrapBlock()

    def stop(self):
        '''Maps to the CLI command and stop the running Wishbone processes.
        '''

        try:
            pid = PIDFile(self.pid)
            sys.stdout.write("Stopping instance with PID ")
            sys.stdout.flush()
            for entry in pid.read():
                sys.stdout.write(" %s " % (entry))
                sys.stdout.flush()
                pid.sendSigint(entry)
            pid.cleanup()
            print("")
        except Exception as err:
            print("")
            print(("Failed to stop instances.  Reason: %s" % (err)))

    def __expandSearchPath(self, module_path):
        for d in module_path.split(','):
            sys.path.append(d.strip())


def main():
    try:
        BootStrap()
    except Exception as err:
        print(("Failed to bootstrap instance.  Reason: %s" % (err)))

if __name__ == '__main__':
    main()
