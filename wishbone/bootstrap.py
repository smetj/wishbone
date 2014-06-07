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
from gevent import sleep, signal
from wishbone.router import Default

class Module():

    def __init__(self):
        pass

    def extractSummary(self, entrypoint):
        try:
            doc=entrypoint.load().__doc__
        except Exception as err:
            return "! -> Unable to load.  Reason: %s"%(err)
        try:
            return re.search('.*?\*\*(.*?)\*\*', doc, re.DOTALL ).group(1)
        except:
            return "No description found."

    def getVersion(self, entrypoint):
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

class Config():

    def __init__(self):
        pass

    def load(self, filename):

        try:
            with open (filename, 'r') as f:
                return yaml.load(f)
        except Exception as err:
            print "Failed to load config file.  Reason: %s"%(err)
            sys.exit(1)

class Dispatch():

    def __init__(self):
        signal(2, self.stop)
        self.module = Module()
        self.config = Config()

    def block(self):

        while True:
            sleep(1)

    def debug(self, command, config, instances):

        config = self.config.load(config)
        self.router = Default()
        self.setupModules(config["modules"])
        self.setupRoutes(config["routingtable"])


        #In debug mode we write our logs to STDOUT
        log_stdout = self.loadModule("wishbone.output.stdout")
        log_human = self.loadModule("wishbone.logging.humanlogformat")
        self.router.initializeModule(log_stdout, "log_stdout")
        self.router.initializeModule(log_human, "log_format")
        self.router.pool.getModule("logs_funnel").connect("outbox", self.router.pool.getModule("log_format"), "inbox")
        self.router.pool.getModule("log_format").connect("outbox", self.router.pool.getModule("log_stdout"), "inbox")

        self.router.start()
        self.block()

    def loadModule(self, name):

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
            sm, sq, dm, dq = self.splitRoute(route)
            self.router.pool.getModule(sm).connect(sq, self.router.pool.getModule(dm), dq)

    def splitRoute(self, definition):
        '''Splits the route definition into 4 separate parts.'''

        (source, destination) = definition.split('->')
        (sm, sq) = source.rstrip().lstrip().split('.')
        (dm, dq) = destination.rstrip().lstrip().split('.')
        return sm, sq, dm, dq

    def start(self):

        self.router.start()

    def stop(self):

        self.router.stop()
        sys.exit(0)

class BootStrap():

    def __init__(self, description="Wishbone bootstrap server."):

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

def main():
    bootstrap = BootStrap()

if __name__ == '__main__':
    main()

