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

from wishbone.router import Default
from wishbone.error import QueueConnected
from wishbone.utils import BootstrapFile, Module, PIDFile
from wishbone import ModuleManager

import argparse
import multiprocessing
import os
import sys
from daemon import DaemonContext
from gevent import sleep, signal
from pkg_resources import get_distribution


class BootStrap():

    '''
    Parses command line arguments and bootstraps the Wishbone instance.
    '''

    def __init__(self, description="Wishbone bootstrap server. Build event pipeline servers with minimal effort.", include_groups=[]):

        parser = argparse.ArgumentParser(description=description)
        subparsers = parser.add_subparsers(dest='command')

        start = subparsers.add_parser('start', description="Starts a Wishbone instance and detaches to the background.  Logs are written to syslog.")
        start.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        start.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        start.add_argument('--pid', type=str, dest='pid', default='%s/wishbone.pid' % (os.getcwd()), help='The pidfile to use.')
        start.add_argument('--queue-size', type=int, dest='queue_size', default=100, help='The queue size to use.')
        start.add_argument('--frequency', type=int, dest='frequency', default=1, help='The metric frequency.')
        start.add_argument('--id', type=str, dest='ident', default=None, help='An identification string.')

        debug = subparsers.add_parser('debug', description="Starts a Wishbone instance in foreground and writes logs to STDOUT.")
        debug.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        debug.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        debug.add_argument('--queue-size', type=int, dest='queue_size', default=100, help='The queue size to use.')
        debug.add_argument('--frequency', type=int, dest='frequency', default=1, help='The metric frequency.')
        debug.add_argument('--id', type=str, dest='ident', default=None, help='An identification string.')

        stop = subparsers.add_parser('stop', description="Tries to gracefully stop the Wishbone instance.")
        stop.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        kill = subparsers.add_parser('kill', description="Kills the Wishbone processes immediately.")
        kill.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        llist = subparsers.add_parser('list', description="Lists the available Wishbone modules.")
        llist.add_argument('--group', type=str, dest='group', default=[], help='List the modules of this group type.')

        show = subparsers.add_parser('show', description="Shows the details of a module.")
        show.add_argument('--module', type=str, help='Shows the documentation of the module. ')

        arguments = vars(parser.parse_args())

        if arguments["command"] == "list":
            if include_groups != []:
                arguments["include_groups"] = include_groups
            else:
                arguments["include_groups"] = [arguments["group"]]

        dispatch = Dispatch()
        getattr(dispatch, arguments["command"])(**arguments)


class Dispatch():

    '''
    Handles the Wishbone instance commands.
    '''

    def __init__(self):

        self.config = BootstrapFile()
        self.routers = []
        signal(2, self.__stopSequence)
        self.__stopping = False
        self.module_manager = ModuleManager()

    def generateHeader(self):
        '''
        Prints a header.
        '''

        return """          __       __    __
.--.--.--|__.-----|  |--|  |--.-----.-----.-----.
|  |  |  |  |__ --|     |  _  |  _  |     |  -__|
|________|__|_____|__|__|_____|_____|__|__|_____|
                                   version %s

Build event pipeline servers with minimal effort.

""" % (get_distribution('wishbone').version)

    def debug(self, command, config, instances, queue_size, frequency, ident):
        '''
        Handles the Wishbone debug command.
        '''

        config = self.config.load(config)

        if instances == 1:
            self.routers.append(RouterBootstrap(config, debug=True, queue_size=queue_size, frequency=frequency, ident=ident))
            self.routers[-1].start()

        else:
            for x in xrange(instances):
                self.routers.append(RouterBootstrapProcess(config, debug=True, queue_size=queue_size, frequency=frequency, ident=ident))
                self.routers[-1].start()

            while multiprocessing.active_children():
                sleep(1)

        sys.exit(0)

    def list(self, command, group, category=None, include_groups=[]):

        print self.generateHeader()
        print "Available modules:"
        print self.module_manager.getModuleTable(category, group, include_groups)

    def show(self, command, module):
        '''
        Shows the help message of a module.
        '''

        print self.generateHeader()
        try:
            (category, group, module) = module.split('.')
        except ValueError:
            (category, sub, group, module) = module.split('.')
            category = "%s.%s" % (category, sub)

        try:
            title = self.module_manager.getModuleTitle(category, group, module)
            version = self.module_manager.getModuleVersion(category, group, module)
            header = "%s.%s.%s" % (category, group, module)
            print
            print "="*len(header)
            print header
            print "="*len(header)
            print
            print "Version: %s" % (version)
            print
            print title
            print "-"*len(title)
            print self.module_manager.getModuleDoc(category, group, module)
        except Exception:
            print "Failed to load module %s.%s.%s." % (category, group, module)

    def start(self, command, config, instances, pid, queue_size, frequency, ident):
        '''
        Handles the Wishbone start command.
        '''

        config = self.config.load(config)
        self.pid = PIDFile(pid)

        if instances == 1:
            print ("Starting 1 instance to background with pid %s." % (os.getpid()))
            try:
                with DaemonContext(stdout=sys.stdout, stderr=sys.stderr, files_preserve=self.__getCurrentFD(), detach_process=True):
                    self.pid.create([os.getpid()])
                    instance = RouterBootstrap(config, debug=False, queue_size=queue_size, frequency=frequency, ident=ident)
                    instance.start()
            except Exception as err:
                sys.stdout.write("Failed to start instance.  Reason: %s\n" % (err))
        else:
            try:
                print "Starting %s instances in background." % (instances)
                with DaemonContext(stdout=sys.stdout, stderr=sys.stderr, files_preserve=self.__getCurrentFD(), detach_process=True):
                    pids = []
                    processes = []
                    for counter in xrange(instances):
                        processes.append(RouterBootstrapProcess(config, debug=False, queue_size=queue_size, frequency=frequency, ident=ident))
                        processes[-1].start()
                        pids.append(processes[-1].pid)
                    self.pid.create(pids)
                    for process in processes:
                        process.join()

            except Exception as err:
                sys.stdout.write("Failed to start instance.  Reason: %s\n" % (err))

    def stop(self, command, pid):
        '''
        Handles the Wishbone stop command.
        '''

        try:
            pid = PIDFile(pid)
            sys.stdout.write("Stopping instance with PID ")
            sys.stdout.flush()
            for entry in pid.read():
                sys.stdout.write(" %s " % (entry))
                sys.stdout.flush()
                pid.sendSigint(entry)
            pid.cleanup()
            print("")
        except Exception as err:
            print ("")
            print ("Failed to stop instances.  Reason: %s" % (err))

    def __stopSequence(self):
        '''
        Calls the stop() function of each instance.
        '''

        if not self.__stopping:
            # TODO: Weird hack, otherwise when trapping signal(2) this function is
            #      executed many times.
            self.__stopping = True
            for instance in self.routers:
                if hasattr(instance, "stop"):
                    instance.stop()

    def __getCurrentFD(self):
        '''
        returns a list with filedescriptors in use.
        '''

        try:
            return [int(x) for x in os.listdir("/proc/self/fd")]
        except Exception as err:
            print ("Failed to get active filedescriptors.  Reason: %s." % (err))
            sys.exit(1)

    def __alive(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except:
            False


class RouterBootstrapProcess(multiprocessing.Process):

    '''
    Wraps RouterBootstrap into a Process class.
    '''

    def __init__(self, config, debug=False, queue_size=100, frequency=1, ident=None):
        multiprocessing.Process.__init__(self)
        self.config = config
        self.ident = ident
        self.debug = debug
        self.queue_size = queue_size
        self.daemon = True

    def run(self):
        '''
        Executed by Process when started.
        '''

        router = RouterBootstrap(self.config, self.debug, self.queue_size, self.frequency, self.ident)
        router.start()


class RouterBootstrap():

    '''
    Setup, configure and a router process.
    '''

    def __init__(self, config, debug=False, queue_size=100, frequency=1, ident=None):
        self.config = config
        self.ident = ident
        self.debug = debug
        self.router = Default(size=queue_size, frequency=frequency)
        self.module = Module()

    def loadModule(self, name):
        '''
        Loads a module using the entrypoint name.
        '''

        return self.module.load(name)

    def setupModules(self, modules):
        '''
        Loads and initialzes the modules from the bootstrap file.
        '''

        for module in modules:
            m = self.loadModule(modules[module]["module"])
            if "arguments" in modules[module]:
                self.router.registerModule(m, module, **modules[module]["arguments"])
            else:
                self.router.registerModule(m, module)

    def setupRoutes(self, table):
        '''
        Connects the modules from the bootstrap file.
        '''

        for route in table:
            sm, sq, dm, dq = self.__splitRoute(route)
            self.router.pool.getModule(sm).connect(sq, self.router.pool.getModule(dm), dq)

    def start(self):
        '''
        Calls the router's start() function.
        '''

        self.setupModules(self.config["modules"])
        self.setupRoutes(self.config["routingtable"])

        if self.debug:
            self.__debug()

        try:
            syslog = self.loadModule("wishbone.output.syslog")
            self.router.registerModule(syslog, "syslog", ident=self.ident)
            self.router.pool.getModule("logs_funnel").connect("outbox", self.router.pool.getModule("syslog"), "inbox")
        except QueueConnected:
            pass

        self.router.start()
        while self.router.isRunning():
            sleep(1)

    def stop(self):
        '''
        Calls the router's stop() function.
        '''

        self.router.stop()

    def __debug(self):
        '''
        In debug mode we route all logging to SDOUT.
        '''

        # In debug mode we write our logs to STDOUT
        log_stdout = self.loadModule("wishbone.output.stdout")
        log_human = self.loadModule("wishbone.encode.humanlogformat")
        self.router.registerModule(log_stdout, "log_stdout")
        self.router.registerModule(log_human, "log_format", ident=self.ident)
        self.router.pool.getModule("logs_funnel").connect("outbox", self.router.pool.getModule("log_format"), "inbox")
        self.router.pool.getModule("log_format").connect("outbox", self.router.pool.getModule("log_stdout"), "inbox")

    def __splitRoute(self, definition):
        '''
        Splits the route definition string into 4 separate string.
        '''

        (source, destination) = definition.split('->')
        (sm, sq) = source.rstrip().lstrip().split('.')
        (dm, dq) = destination.rstrip().lstrip().split('.')
        return sm, sq, dm, dq


def main():
    try:
        BootStrap()
    except Exception as err:
        print "Failed to bootstrap instance.  Reason: %s" % (err)

if __name__ == '__main__':
    main()
