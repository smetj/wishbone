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
import os
import yaml
import multiprocessing
from daemon import DaemonContext, pidfile
from gevent import sleep, signal
from wishbone.router import Default


class BootStrap():
    '''Bootstraps a Wishbone instance.'''

    def __init__(self, description="Wishbone bootstrap server. Building async event pipeline servers."):

        parser = argparse.ArgumentParser(description=description)
        subparsers = parser.add_subparsers(dest='command')

        start = subparsers.add_parser('start', description="Starts a Wishbone instance and detaches to the background.  Logs are written to syslog.")
        start.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        start.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        start.add_argument('--pid', type=str, dest='pid', default='%s/wishbone.pid' % (os.getcwd()), help='The pidfile to use.')

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

        arguments = vars(parser.parse_args())

        dispatch = Dispatch()
        getattr(dispatch, arguments["command"])(**arguments)


class BootstrapFile():
    '''Handles bootstrap file interaction'''

    def __init__(self):
        pass

    def load(self, filename):
        '''Loads and returns the yaml bootstrap file.'''

        try:
            with open(filename, 'r') as f:
                config = yaml.load(f)
        except Exception as err:
            print "Failed to load config file.  Reason: %s" % (err)
            sys.exit(1)

        try:
            return self.verify(config)
        except Exception as err:
            print "Syntax error in bootstrap file. Reason: %s" % (err)
            sys.exit(1)

    def verify(self, content):
        assert "routingtable" in content, "'routingtable' section not found in bootstrap file."
        assert "modules" in content, "'modules' section not found in bootstrap file."

        return content


class PIDFile():
    '''Handles all PIDfile interactions'''

    def __init__(self, location):
        self.location = location

    def create(self, pids=[]):
        '''Creates the pidfile containing the provided list of pids.'''

        if self.exists():
            if self.valid():
                raise Exception("Pidfile exists and at least one process running.")
            else:
                self.__deletePIDFile()

        self.__writePIDFile(pids)

    def valid(self):
        '''Returns True at least one PID within pidfile is still alive.'''

        try:
            for pid in self.__readPIDFile():
                if self.__isAlive(pid):
                    return True
            return False
        except Exception as err:
            return False

    def exists(self):
        '''Returns True if file exists.'''

        return os.path.isfile(self.location)

    def __isAlive(self, pid):
        '''Verifies whether pid is still alive.'''

        try:
            os.kill(pid, 0)
            return True
        except:
            False

    def __writePIDFile(self, pids=[]):
        '''Writes a list pids to the file.'''

        with open(self.location, 'w') as pidfile:
            for pid in pids:
                pidfile.write("%s\n" % (pid))

    def __readPIDFile(self):
        '''Returns a list of pids values the file contains.'''

        with open(self.location, 'r') as pidfile:
            pids = pidfile.readlines()

        return pids

    def __deletePIDFile(self):
        '''Unconditionally deletes the pidfile.'''

        if os.path.isfile(self.location):
            os.remove(self.location)


class Dispatch():
    '''Handles the Wishbone instance commands.'''

    def __init__(self):

        self.config = BootstrapFile()
        self.instances = []
        signal(2, self.__stopSequence)
        self.__stopping = False

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

            while multiprocessing.active_children():
                sleep(1)

        sys.exit(0)

    def start(self, command, config, instances, pid):
        '''Handles the Wishbone start command.'''

        config = self.config.load(config)
        pid = PIDFile(pid)

        if instances == 1:
            with DaemonContext(
                    stdout=open('stdout.txt', 'w+'),
                    stderr=open('stderr.txt', 'w+'),
                    files_preserve=self.__getCurrentFD(),
                    detach_process=True,
                    working_directory=os.getcwd()):
                        self.instances.append(RouterBootstrap(config, debug=True))
                        self.instances[-1].start()
                        self.pid.create([os.getpid()])
        else:
            print "not implemented yet"

    def stop(self, command, pid):
        '''Handles the Wishbone stop command.'''

        pass

    def __stopSequence(self):

        if not self.__stopping:
            # TODO: Weird hack, otherwise when trapping signal(2) this function is
            #      executed many times.
            self.__stopping = True
            for instance in self.instances:
                if hasattr(instance, "stop"):
                    instance.stop()
                else:
                    os.kill(instance.pid, 2)

    def __getCurrentFD(self):
        '''returns a list with filedescriptors in use.'''

        try:
            return [int(x) for x in os.listdir("/proc/self/fd")]
        except Exception as err:
            print "Failed to get active filedescriptors.  Reason: %s." % (err)
            sys.exit(1)


class Module():
    '''Handles all Wishbone module interaction.'''

    def __init__(self):
        pass

    def extractSummary(self, entrypoint):
        '''Extracts and returns a module's docstring using the entrypoint'''

        try:
            doc = entrypoint.load().__doc__
        except Exception as err:
            return "! -> Unable to load.  Reason: %s" % (err)
        try:
            return re.search('.*?\*\*(.*?)\*\*', doc, re.DOTALL).group(1)
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

        e = entrypoint.split('.')
        name = e[-1]
        del(e[-1])
        group = ".".join(e)
        module_instance = None

        for module in pkg_resources.iter_entry_points(group=group, name=name):
            try:
                module_instance = module.load()
            except Exception as err:
                raise Exception("Problem loading module %s  Reason: %s" % (module, err))

        if module_instance is not None:
            return module_instance
        else:
            raise Exception("Failed to load module %s  Reason: Not found" % (entrypoint))


class RouterBootstrapProcess(multiprocessing.Process):
    '''Wraps RouterBootstrap into a Process class.'''

    def __init__(self, config, debug=False):
        multiprocessing.Process.__init__(self)
        self.config = config
        self.debug = debug
        self.daemon = True

    def run(self):
        router = RouterBootstrap(self.config, self.debug)
        router.start()


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
            if "arguments" in modules[module]:
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

        if self.debug:
            self.__debug()

        self.router.start()

        while self.router.isRunning():
            sleep(1)

    def stop(self):
        self.router.stop()

    def __debug(self):
        '''In debug mode we route all logging to SDOUT.'''

        # In debug mode we write our logs to STDOUT
        log_stdout = self.loadModule("wishbone.output.stdout")
        log_human = self.loadModule("wishbone.logging.humanlogformat")
        self.router.initializeModule(log_stdout, "log_stdout")
        self.router.initializeModule(log_human, "log_format")
        self.router.pool.getModule("logs_funnel").connect("outbox", self.router.pool.getModule("log_format"), "inbox")
        self.router.pool.getModule("log_format").connect("outbox", self.router.pool.getModule("log_stdout"), "inbox")

    def __splitRoute(self, definition):
        '''Splits the route definition string into 4 separate string.
        '''

        (source, destination) = definition.split('->')
        (sm, sq) = source.rstrip().lstrip().split('.')
        (dm, dq) = destination.rstrip().lstrip().split('.')
        return sm, sq, dm, dq


def main():
    bootstrap = BootStrap()

if __name__ == '__main__':
    main()
