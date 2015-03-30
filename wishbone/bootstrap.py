#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bootstrap.py
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

import argparse
import os
import sys

from wishbone.router import Default
from wishbone import ModuleManager
from wishbone.config import ConfigFile
from wishbone.utils import PIDFile
from gevent import signal
from daemon import DaemonContext
from pkg_resources import get_distribution
from jinja2 import Template


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
        start.add_argument('--id', type=str, dest='identification', default=None, help='An identification string.')

        debug = subparsers.add_parser('debug', description="Starts a Wishbone instance in foreground and writes logs to STDOUT.")
        debug.add_argument('--config', type=str, dest='config', default='wishbone.cfg', help='The Wishbone bootstrap file to load.')
        debug.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Wishbone instances to bootstrap.')
        debug.add_argument('--queue-size', type=int, dest='queue_size', default=100, help='The queue size to use.')
        debug.add_argument('--frequency', type=int, dest='frequency', default=1, help='The metric frequency.')
        debug.add_argument('--id', type=str, dest='identification', default=None, help='An identification string.')

        stop = subparsers.add_parser('stop', description="Tries to gracefully stop the Wishbone instance.")
        stop.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        kill = subparsers.add_parser('kill', description="Kills the Wishbone processes immediately.")
        kill.add_argument('--pid', type=str, dest='pid', default='wishbone.pid', help='The pidfile to use.')

        llist = subparsers.add_parser('list', description="Lists the available Wishbone modules.")
        llist.add_argument('--group', type=str, dest='group', default=None, help='List the modules of this group type.')

        show = subparsers.add_parser('show', description="Shows the details of a module.")
        show.add_argument('--module', type=str, required=True, help='Shows the documentation of the module. ')

        arguments = vars(parser.parse_args())

        if arguments["command"] == "list":
            if arguments["group"] is not None:
                arguments["include_groups"] = [arguments["group"]]
            else:
                arguments["include_groups"] = include_groups

        dispatch = Dispatch()
        getattr(dispatch, arguments["command"])(**arguments)


class Dispatch():

    '''
    Handles the Wishbone instance commands.
    '''

    def __init__(self):

        self.routers = []
        self.__stopping = False

    def generateHeader(self):
        '''Generates the Wishbone ascii header.'''

        with open("%s/data/banner.tmpl" % (os.path.dirname(__file__))) as f:
            template = Template(''.join(f.readlines()))

        return template.render(version=get_distribution('wishbone').version)

    def debug(self, command, config, instances, queue_size, frequency, identification):
        '''
        Handles the Wishbone debug command.
        '''

        processes = []

        def stopSequence():
            for proc in processes:
                proc.stop()

        signal(2, stopSequence)

        module_manager = ModuleManager()
        router_config = ConfigFile().load(config)

        if instances == 1:
            sys.stdout.write("\nInstance started in foreground with pid %s\n" % (os.getpid()))
            Default(router_config, module_manager, size=queue_size, frequency=frequency, identification=identification, stdout_logging=True).start()
        else:
            for instance in range(instances):
                processes.append(Default(router_config, module_manager, size=queue_size, frequency=frequency, identification=identification, stdout_logging=True, process=True).start())
            pids = [str(p.pid) for p in processes]
            print("\nInstances started in foreground with pid %s\n" % (", ".join(pids)))
            for proc in processes:
                proc.join()

    def list(self, command, group, category=None, include_groups=[]):

        print self.generateHeader()
        print "Available modules:"
        print ModuleManager().getModuleTable(category, group, include_groups)

    def show(self, command, module):
        '''
        Shows the help message of a module.
        '''

        module_manager = ModuleManager()
        module_manager.validateModuleName(module)
        module_manager.exists(module)

        print self.generateHeader()
        try:
            (category, group, module) = module.split('.')
        except ValueError:
            (category, sub, group, module) = module.split('.')
            category = "%s.%s" % (category, sub)


        try:
            title = module_manager.getModuleTitle(category, group, module)
            version = module_manager.getModuleVersion(category, group, module)
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
            print module_manager.getModuleDoc(category, group, module)
        except Exception as err:
            print "Failed to load module %s.%s.%s. Reason: %s" % (category, group, module, err)

    def start(self, command, config, instances, pid, queue_size, frequency, identification):
        '''
        Handles the Wishbone start command.
        '''

        module_manager = ModuleManager()
        router_config = ConfigFile().load(config)
        pid_file = PIDFile(pid)

        with DaemonContext(stdout=sys.stdout, stderr=sys.stderr, files_preserve=self.__getCurrentFD(), detach_process=True):
            if instances == 1:
                sys.stdout.write("\nWishbone instance started with pid %s\n" % (os.getpid()))
                pid_file.create([os.getpid()])
                Default(router_config, module_manager, size=queue_size, frequency=frequency, identification=identification, stdout_logging=False).start()
            else:
                processes = []
                for instance in range(instances):
                    processes.append(Default(router_config, module_manager, size=queue_size, frequency=frequency, identification=identification, stdout_logging=False, process=True).start())
                pids = [str(p.pid) for p in processes]
                print("\n%s Wishbone instances started in background with pid %s\n" % (len(pids), ", ".join(pids)))
                pid_file.create(pids)
                for proc in processes:
                    proc.join()

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


def main():
    BootStrap()
    # try:
    #     BootStrap()
    # except Exception as err:
    #     print "Failed to bootstrap instance.  Reason: %s" % (err)

if __name__ == '__main__':
    main()
