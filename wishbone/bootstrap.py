#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bootstrap.py
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

import argparse
import pkg_resources
import sys
import yaml
import daemon
from gevent import signal, sleep
from multiprocessing import Process
from wishbone.router import Default


class BootStrap():
    '''Bootstraps a Wishbone instance.'''

    def __init__(self, description="Wishbone bootstrap server. Building async event pipeline servers."):

        parser = argparse.ArgumentParser(description=description)
        subparsers = parser.add_subparsers(dest='command')

        start = subparsers.add_parser('start', description="Starts a Wishbone instance and detaches to the background.  Logs are written to syslog.")
        start.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        start.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        start.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        debug = subparsers.add_parser('debug', description="Starts a Wishbone instance in foreground and writes logs to STDOUT.")
        debug.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        debug.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')

        stop = subparsers.add_parser('stop', description="Tries to gracefully stop the Wishbone instance.")
        stop.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        kill = subparsers.add_parser('kill', description="Kills the Wishbone processes immediately.")
        kill.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        llist = subparsers.add_parser('list', description="Lists the available Wishbone modules.")
        llist.add_argument('--group', type=str, dest='group', default=None, help='List the modules of this group type.')

        show = subparsers.add_parser('show', description="Shows the details of a module.")
        show.add_argument('module', type=str, help='Shows the documentation of the module. ')

        arguments=vars(parser.parse_args())

        dispatch=Dispatch()
        getattr(dispatch, arguments["command"])(**arguments)

class Config():
    '''Handles bootstrap file interaction'''

    def __init__(self):
        pass

    def load(self, filename):
        '''Loads and returns the yaml bootstrap file.'''

        try:
            with open (filename, 'r') as f:
                return yaml.load(f)
        except Exception as err:
            print "Failed to load config file.  Reason: %s"%(err)
            sys.exit(1)

class Dispatch():
    '''Handles the Wishbone instance commands.'''

    def __init__(self):
        signal(2, self.stop)
        self.config = Config()
        self.instances = []

    def debug(self, command, config, instances):
        '''Handles the Wishbone debug command.'''

        config = self.config.load(config)

        if instances == 1:
            self.instances.append(RouterBootstrap(config, debug=True))
            self.instances[-1].start()

        else:
            for x in xrange(instances):
                self.instances.append(RouterBootstrapProcess(config, debug=True))
                self.instances[-1].start()
            while True:
                sleep(1)

    def start(self, command, config, instances):
        '''Handles the Wishbone start command.'''

        self.router.start()

    def stop(self):
        '''Handles the Wishbone stop command.'''

        for instance in self.instances:
            instance.stop()
        sys.exit(0)

class Module():
    '''Handles all Wishbone module interaction.'''

    def __init__(self):
        pass

    def extractSummary(self, entrypoint):
        '''Extracts and returns a module's docstring using the entrypoint'''

        try:
            doc=entrypoint.load().__doc__
        except Exception as err:
            return "! -> Unable to load.  Reason: %s"%(err)
        try:
            return re.search('.*?\*\*(.*?)\*\*', doc, re.DOTALL ).group(1)
        except:
            return "No description found."

    def getVersion(self, entrypoint):
        '''Extracts and returns a module's version.'''

        modulename = vars(entrypoint)["module_name"].split('.')[0]

        try:
            return pkg_resources.get_distribution(modulename).version
        except Exception as err:
            return "Unknown"

    def load(self, entrypoint):
        '''Loads a module from an entrypoint string and returns it.'''

        e=entrypoint.split('.')
        name=e[-1]
        del(e[-1])
        group=".".join(e)
        module_instance=None

        for module in pkg_resources.iter_entry_points(group=group, name=name):
            try:
                module_instance=module.load()
            except Exception as err:
                raise Exception ("Problem loading module %s  Reason: %s"%(module, err))

        if module_instance != None:
            return module_instance
        else:
            raise Exception ("Failed to load module %s  Reason: Not found"%(entrypoint))

class RouterBootstrapProcess(Process):
    '''Wraps RouterBootstrap into a Process class.'''

    def __init__(self, config, debug=False):
        Process.__init__(self)
        self.config = config
        self.debug = debug
        self.daemon = True
        self.r = RouterBootstrap(self.config, self.debug)

    def run(self):
        self.r.start()

    def stop(self):
        self.r.stop()

class RouterBootstrap():
    '''Setup, configure, run and optionally daemonize a router process.'''

    def __init__(self, config, debug=False):
        self.config = config
        self.debug = debug
        self.router = Default()
        self.module = Module()

    def loadModule(self, name):
        '''Loads a module using the entrypoint name.'''

        return self.module.load(name)

    def setupModules(self, modules):
        '''Loads and initialzes the modules from the bootstrap file.'''

        for module in modules:
            m = self.loadModule(modules[module]["module"])
            if modules[module].has_key("arguments"):
                self.router.initializeModule(m, module, **modules[module]["arguments"])
            else:
                self.router.initializeModule(m, module)

    def setupRoutes(self, table):
        '''Connects the modules from the bootstrap file.'''

        for route in table:
            sm, sq, dm, dq = self.__splitRoute(route)
            self.router.pool.getModule(sm).connect(sq, self.router.pool.getModule(dm), dq)

    def start(self):
        '''Calls the router's start() function.
        '''

        self.setupModules(self.config["modules"])
        self.setupRoutes(self.config["routingtable"])

        if self.debug == True:
            self.__debug()

        self.router.start()
        self.router.block()

    def stop(self):
        '''Calls the router's stop() function.'''

        self.router.stop()

    def __debug(self):
        '''In debug mode we route all logging to SDOUT.'''

        #In debug mode we write our logs to STDOUT
        log_stdout = self.loadModule("wishbone.output.stdout")
        log_human = self.loadModule("wishbone.logging.humanlogformat")
        self.router.initializeModule(log_stdout, "log_stdout")
        self.router.initializeModule(log_human, "log_format")
        self.router.pool.getModule("logs_funnel").connect("outbox", self.router.pool.getModule("log_format"), "inbox")
        self.router.pool.getModule("log_format").connect("outbox", self.router.pool.getModule("log_stdout"), "inbox")

    def __splitRoute(self, definition):
        '''Splits the route definition into 4 separate parts.'''

        (source, destination) = definition.split('->')
        (sm, sq) = source.rstrip().lstrip().split('.')
        (dm, dq) = destination.rstrip().lstrip().split('.')
        return sm, sq, dm, dq

def main():
    bootstrap = BootStrap()

if __name__ == '__main__':
    main()

