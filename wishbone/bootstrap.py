#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bootstrap.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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

from gevent import monkey; monkey.patch_all()
import gipc
import argparse
import os
import sys
# http://stackoverflow.com/questions/4554271/how-to-avoid-excessive-stat-etc-localtime-calls-in-strftime-on-linux
os.environ["TZ"] = ":/etc/localtime"

from wishbone.router.default import Default
from wishbone.componentmanager import ComponentManager
from wishbone.config import ConfigFile
from wishbone.utils import PIDFile
from gevent import signal
from gevent.event import Event
from daemon import DaemonContext
from pkg_resources import get_distribution


class BootStrap():
    '''
    Parses command line arguments and bootstraps the Wishbone instance.
    '''

    def __init__(self, description="Pragmatic event processing servers.", include_groups=[]):

        parser = argparse.ArgumentParser(description=description)
        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = True

        start = subparsers.add_parser('start', description="Bootsraps a Wishbone instance.")
        start.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        start.add_argument('--frequency', type=int, dest='frequency', default=10, help='The metric frequency.')
        start.add_argument('--graph', action="store_true", dest="graph", help='When enabled starts a webserver on 8088 showing a graph of connected modules and queues.')
        start.add_argument('--graph-include-sys', action="store_true", dest="graph_include_sys", help='When enabled includes logs and metrics related queues modules and queues to graph layout.')
        start.add_argument('--identification', type=str, dest='identification', default="wishbone", help='An identifier string for generated logs.')
        start.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        start.add_argument('--loglevel', type=int, dest='log_level', default=6, help='The maximum loglevel.')
        start.add_argument('--fork', action="store_true", default=False, help="When defined forks Wishbone to background and INFO logs are written to syslog/journald.")
        start.add_argument('--nocolor', action="store_true", help='When defined does not print colored output to stdout.')
        start.add_argument('--pid', type=str, dest='pid', default='%s/wishbone.pid' % (os.getcwd()), help='The pidfile to use.')
        start.add_argument('--profile', action="store_true", help='When enabled profiles the process and dumps a Chrome developer tools profile file in the current directory.')
        start.add_argument('--queue-size', type=int, dest='queue_size', default=100, help='The queue size to use.')

        stop = subparsers.add_parser('stop', description="Tries to gracefully stop the Wishbone instance.")
        stop.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        list = subparsers.add_parser('list', description="Lists the available modules.")
        list.add_argument('--namespace', type=str, dest='namespace', default="wishbone, wishbone_contrib, wishbone_external", help='The component namespace to query.')

        show = subparsers.add_parser('show', description="Shows information about a component.")
        show_group = show.add_mutually_exclusive_group(required=True)
        show_group.add_argument('--docs', type=str, help='Shows the documentation of the component.')
        show_group.add_argument('--code', type=str, help='Shows the code of the refered component.')

        arguments = vars(parser.parse_args())

        dispatch = Dispatch(**arguments)
        getattr(dispatch, arguments["command"])()


class Dispatch():
    '''
    Handles the Wishbone commands, processes and daemons.
    '''

    def __init__(self, **kwargs):
        self.command = kwargs.get("command", None)
        self.config = kwargs.get("config", None)
        self.instances = kwargs.get("instances", None)
        self.pid = kwargs.get("pid", None)
        self.queue_size = kwargs.get("queue_size", None)
        self.frequency = kwargs.get("frequency", None)
        self.identification = kwargs.get("identification", None)
        self.graph = kwargs.get("graph", None)
        self.graph_include_sys = kwargs.get("graph_include_sys", None)
        self.profile = kwargs.get("profile", None)
        self.docs = kwargs.get("docs", None)
        self.code = kwargs.get("code", None)
        self.nocolor = kwargs.get("nocolor", False)
        self.fork = kwargs.get("fork", None)
        self.log_level = kwargs.get("log_level", None)
        self.namespace = kwargs.get("namespace", None)
        self.routers = []

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

    def initializeOneRouter(self, config):
        '''Initializes a Router instance using the provided config object.

        This function blocks until signal(2) is received after which it
        continues and executes the router's stop() method.

        The idea is that you can spawn this function to the background to have
        multiple parallel instances.

        Args:
            config (Wishbone.config.configfile:ConfigFile): The router configuration
        '''

        def startRouter():
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
        signal(2, e.set)

        if self.profile:
            from wishbone.utils.py2devtools import Profiler
            with Profiler():
                startRouter()
        else:
            startRouter()

    def initializeManyRouters(self, config, number, background):

        '''Initialize many routers and background if required

        Args:
            config (Wishbone.config.configfile:ConfigFile): The router configration
            number (int): The number of instances to intialize
            background (bool): Whether to background the routers or not
        '''

        if background:
            pid_file = PIDFile(self.pid)
            with DaemonContext(stdout=sys.stdout, stderr=sys.stderr, detach_process=True):
                if self.instances == 1:
                    sys.stdout.write("\nWishbone instance started with pid %s\n" % (os.getpid()))
                    sys.stdout.flush()
                    pid_file.create([os.getpid()])
                    self.initializeOneRouter(config)
                else:
                    for instance in range(self.instances):
                        self.routers.append(
                            gipc.start_process(
                                self.initializeOneRouter,
                                args=(config, ),
                                daemon=True
                            )
                        )

                    pids = [str(p.pid) for p in self.routers]
                    print(("\nInstances started in foreground with pid %s\n" % (", ".join(pids))))
                    pid_file.create(pids)

                self.bootstrapBlock()
        else:
            if self.instances == 1:
                sys.stdout.write("\nInstance started in foreground with pid %s\n" % (os.getpid()))
                self.initializeOneRouter(config)
            else:
                for instance in range(self.instances):
                    self.routers.append(
                        gipc.start_process(
                            self.initializeOneRouter,
                            args=(config, ),
                            daemon=True
                        )
                    )

                pids = [str(p.pid) for p in self.routers]
                print(("\nInstances started in foreground with pid %s\n" % (", ".join(pids))))
                self.bootstrapBlock()

    def list(self):
        '''Maps to the CLI command and lists all Wishbone entrypoint modules it can find.
        '''

        print((self.generateHeader()))
        print((ComponentManager(namespace=[n.strip() for n in self.namespace.split(",")]).getComponentTable()))

    def show(self):
        '''Maps to the CLI command and shows the docstring of the Wishbone module.
        '''

        component_manager = ComponentManager()

        if self.docs is not None:
            component_manager.validateComponentName(self.docs)
            component_manager.exists(self.docs)

            print((self.generateHeader()))
            (namespace, component_type, category, name) = self.docs.split('.')

            try:
                title = component_manager.getComponentTitle(namespace, component_type, category, name)
                version = component_manager.getComponentVersion(namespace, component_type, category, name)
                header = "%s.%s.%s.%s" % (namespace, component_type, category, name)
                print("")
                print(("=" * len(header)))
                print(header)
                print(("=" * len(header)))
                print("")
                print(("Version: %s" % (version)))
                print("")
                print(title)
                print(("-" * len(title)))
                print((component_manager.getComponentDoc(namespace, component_type, category, name)))
            except Exception as err:
                print("Failed to load component '%s'. Reason: %s" % (self.docs, err))

        if self.code is not None:

            component_manager.validateComponentName(self.code)
            component_manager.exists(self.code)

            import inspect
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import terminal

            component = component_manager.getComponentByName(self.code)
            code = "".join(inspect.getsourcelines(component)[0])
            print(highlight(code, get_lexer_by_name("python"), terminal.TerminalFormatter()))

    def start(self):
        '''Maps to the CLI command and starts one or more Wishbone processes in background.
        '''

        colorize = not self.nocolor

        if self.fork:
            logstyle = "SYSLOG"
        else:
            logstyle = "STDOUT"

        router_config = ConfigFile(
            filename=self.config,
            logstyle=logstyle,
            loglevel=self.log_level,
            colorize_stdout=colorize,
            identification=self.identification
        )
        config = router_config.dump()

        self.initializeManyRouters(
            config=config,
            number=self.instances,
            background=self.fork
        )

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


def main():
    try:
        BootStrap()
    except Exception as err:
        print(("Failed to bootstrap instance.  Reason: %s" % (err)))


if __name__ == '__main__':
    main()
