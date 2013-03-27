#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  server.py
#
#  Copyright 2013 Jelle Smet development@smetj.net
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

import daemon
import json
import sys
import resource
import argparse
import signal
from multiprocessing import Process
from jsonschema import validate
from time import sleep
from os import getpid, kill, remove, path, getpid
from signal import SIGTERM, SIGKILL
from logging import INFO, DEBUG
from wishbone.tools import ConfigureLogging
from wishbone import Wishbone
from pkg_resources import iter_entry_points
from prettytable import PrettyTable

class Help():
    def error(self, message):
        self.message()
        print message
        sys.exit(2)

    def message(self):
        print '%s version %s                                          %s'%(self.name,self.version, self.author)
        print ''
        print '%s'%self.description
        print ''
        print '%s command --config file [--instances number] [--loglevel level] [--pid filename] [--group groupname]'%sys.argv[0]
        print ''
        print '''
        Commands:

            start           Starts and daemonizes the program into the background.
            stop            Stops a daemonized instance.
            debug           Starts the program in the foreground without detaching.
            kill            Kills the daemonized instance.
            list            Lists the available Wishbone modules in group

        Parameters:

            --config        The filename of the bootstrap config file.

            --instances     The number of parallel instances to start. Default is 1.

            --loglevel      Defines the loglevel to use. Default is "info".
                            Possible values are:
                                info, warning, critical, debug

            --pid           Defines the location of the pidfile.
                            The default value is /tmp/%s.pid
            
            --group         The name of the module group to list modules from.'''%(self.name)

        if self.support != '':
            print '''

Support:
        '''
            print "%s"%(self.support)
        print ""

class BootStrap(Help):
    '''**Bootstraps a Wishbone setup using the received configuration.**
            
    Takes care of parsing arguments from command line, reading the bootstrap file
    and initializing the ParallelServer class with the WishboneSkeleton class.
    The accepted parameters are used in the --help output on the CLI.
    
    Parameters:
    
        - name (str):           The name of the WishBone setup.
        - version (str):        The version of the WishBone setup.
        - description (str):    A brief description explaining the setup.
        - author (str):         The name of the author.
        - support (str):        Contains support information.  When emty, no support information is shown.
    '''

    def __init__(self,name="WishBone", version="n/a", description="A WishBone event pipeline setup.", author="Unknown", support=""):

        self.name=name
        self.version=version
        self.description=description
        self.author=author
        self.support=support
        self.allowed_commands=[ "start","stop","debug","kill","list" ]
        self.cli=self.parseArguments()
        self.conf=None
        self.log_level = self.translateLogLevel(self.cli["loglevel"])
        self.do()

    def do(self):
        if self.cli['command'][0] in self.allowed_commands:
            if self.cli['command'][0] == "list":
                for group in self.cli['group'].split(','):
                    modules = PrettyTable(["Entry Point","Module"])
                    modules.align["Entry Point"] = "l"
                    modules.align["Module"] = "l"
                    for module in iter_entry_points(group=group):
                        modules.add_row(str(module).split(" = "))
                    print "\nAvailable Wishbone modules in group %s:\n"%(group)
                    print modules
            else:
                self.conf=self.readConfig(self.cli["config"])
                self.initializeParallelserver()
        else:
            self.error("That commmand does not exist.")

    def parseArguments(self):
        '''Parses the CLI arguments.'''
        
        parser = argparse.ArgumentParser(add_help=False)
        parser.error = self.error
        parser.add_argument('command', nargs=1, help='Which command to issue.  start, stop, kill, debug or list.')
        parser.add_argument('--help', action='store_true', default=False)
        parser.add_argument('--config', dest='config', help='The location of the configuration file.')
        parser.add_argument('--instances', dest='instances', default=1, help='The number of parallel instances to start.')
        parser.add_argument('--loglevel', dest='loglevel', default="info", help='The loglevel you want to use. [info,warn,crit,debug]')
        parser.add_argument('--pid', dest='pid', help='The absolute path of the pidfile.')
        parser.add_argument('--group', dest='group', default="wishbone.iomodule,wishbone.module,wishbone.metrics", help='The entry point group to list the modules from.')
        
        return vars(parser.parse_args())

    def initializeParallelserver(self):
        '''Initializes the parallelserver instance'''
        
        ParallelServer( instances=int(self.cli['instances']),
                    setup=WishbBoneSkeleton,    
                    setup_args=[self.conf],
                    command=self.cli['command'][0],
                    name=self.name,
                    log_level=self.log_level,
                    pidfile=self.cli['pid']
        )

    def readConfig(self,filename):
        try:
            f = open(filename, "r")
            config = f.readlines()
            f.close()
            config = json.loads(''.join(config))
            self.validateConfig(config)
            return config
        except Exception as err:
            print ('An error occurred when processing the config files. Reason: %s'%err)
            sys.exit(1)

    def translateLogLevel(self,loglevel):
        if loglevel == "debug":
            return DEBUG
        elif loglevel == "info":
            return INFO

    def validateConfig(self,config):
        schema={ 
            "type":"object",
            "additionalProperties":False,
            "required":True,
            "properties":{
                "system":{
                    "type":"object",
                    "additionalProperties":False
                    },
                "metrics":{
                    "type":"object",
                    "additionalProperties":False,
                    "required":True,
                    "properties":{
                        "enable":{
                            "type":"boolean"
                        },
                        "group":{
                            "type":"string"
                        },
                        "module":{
                            "type":"string"
                        },
                        "interval":{
                            "type":"integer"
                        },
                        "variables":{
                            "type":"object",
                            "additionalProperties":{
                                "type":"string",
                                "require":False
                            }
                        }
                    }                        
                },
                "bootstrap":{
                    "type":"object",
                    "required":True,
                    "additionalProperties":{
                        "type":"object",
                        "required":True,
                        "additionalProperties":False,
                        "properties":{
                            "group":{
                                "type":"string"
                            },
                            "module":{
                                "type":"string"
                            },
                            "variables":{
                                "type":"object",
                                "additionalProperties":{
                                    "type":["string","integer","boolean"]
                                }
                            }
                        }
                    }
                },
                "routingtable":{
                    "type":"object",
                    "additionalProperties":{
                        "type":"array",
                        "require":True
                    }
                }
            }
        }
        validate(config,schema)
        
class WishbBoneSkeleton():
    '''**Loads, initializes and connects the WishBone modules according to the 
    bootstrap configuration.**
    
    This class is responsible for loading and initializing the WishBone classes
    using the parameter values defined in the bootstrap file.  This class is also
    responsible for creating the module connections.
    
    Parameters:
    
            - conf (dict):      A dictionary containing the bootstrap config file.    
    '''

    def __init__(self, conf):
        self.conf=conf
        try:
            self.wb = self.setup()
        except Exception as err:
            sys.stderr.write("Wishbone library could not be initialized. Reason: %s\n"%str(err))
            sys.exit(1)
        else:
            self.wb.start()

    def setup(self):
        wb = Wishbone()
        for module in self.conf["bootstrap"]:
            wb.loadModule ( (self.conf["bootstrap"][module]["group"],self.conf["bootstrap"][module]["module"],module),
                                **self.conf["bootstrap"][module]["variables"]
            )
        wb.loadMetric(self.conf.get("metrics",False))
        for source in self.conf["routingtable"]:
            for destination in self.conf["routingtable"][source]:
                wb.connect(source,destination)
        return wb

class ParallelServer(ConfigureLogging):
    '''**Handles starting, stopping and daemonizing of one or multiple Wishbone instances.**
    
    ParallelServer handles the work related to starting, stopping, backgrounding
    the WishBone setup.

    Parameters:

        - instances (int):          The number of parallel instances to start.
        - setup (class):            The class containing the WishBone setup. (WishBoneSkeleton)
        - setup_args (list):        *args to initiate the setup class.
        - setup_kwargs (dict):      **kwargs to initiate the setup class.
        - command (string):         Which command to invoke. (start, debug, stop, status)
        - log_level (object):       The loglevel to use
        - name (string):            The name of this insance.
        - pidfile (string):         The absolute pathname of the pidfile.
    '''

    def __init__(self, instances=1, setup=None, setup_args=[], setup_kwargs={}, command=None, log_level=INFO, name='Server', pidfile=None):
        self.instances=instances
        self.setup=setup
        self.setup_kwargs=setup_kwargs
        self.setup_args=setup_args
        self.command=command
        self.log_level=log_level
        self.name=name
        self.wishbone=None
        self.processes=[]
        self.pidfile = self.constructPidFileName(pidfile,name)
        self.pids = None
        self.block=True
        signal.signal(signal.SIGINT, self.sendStop)
        self.do()

    def do(self):
        '''Executes the command.'''
        if self.command == "debug":
            self.initRootLogger(name="ParallelServer",syslog=False,loglevel=self.log_level)
            self.debug()
        elif self.command == "start":
            self.initRootLogger(name="ParallelServer",syslog=True,loglevel=self.log_level)
            self.start()
        elif self.command == "stop":
            self.initRootLogger(name="ParallelServer",syslog=False,loglevel=self.log_level)
            self.stop()
        elif self.command == 'kill':
            self.initRootLogger(name="ParallelServer",syslog=False,loglevel=self.log_level)
            self.kill()

    def debug(self):
        '''Starts the server environment in the foreground.'''
        if self.startPid(self.pidfile):
            self.logging.info('Starting %s in foreground.' % (self.name))
            self.__start()

    def start(self):
        '''Starts the server environment in the background.

        If somebody can figure out which damn filedescriptors get closed by DaemonContext which prevent
        the eventloop to run in detached mode I would be very grateful.
        For the time being I'm preventing all filedescriptors to be closed.
        '''

        if self.startPid(self.pidfile):
            print('Starting %s in background.' % (self.name))
            with daemon.DaemonContext(files_preserve=range(self.getMaximumFileDescriptors())):
                self.__start()

    def __start(self):
        '''Actually starts the environment.  Should only be called by self.start() or self.debug().'''

        for number in range(int(self.instances)):
            self.processes.append(Process(target=self.setup, name=number, args=self.setup_args, kwargs=self.setup_kwargs))
            self.processes[number].start()
            self.logging.info('Instance #%s started.'%number)

        self.writePids(self.collectPids())
        self.logging.info('Started with pids: %s' % ', '.join(map(str, self.pids)))
        while self.block:
            sleep(1)
        self.removePids()

    def sendStop(self, a, b):
        '''Stops the environment by sending sigint to all processes'''
        
        for process in self.processes:
            process.terminate()
            process.join()
        self.block=False       
    
    def stop(self):
        '''Stops the environment.'''
        
        self.logging.info('SIGINT received. Stopping processes gracefully.')
        myself = getpid()
        for pid in self.stopPid(self.pidfile):
            if pid != myself:
                self.sendSIGTERM(pid)
                while self.checkPidAlive(pid):
                    self.sendSIGTERM(pid)
                    self.logging.info('Waiting to exit.')
                    sleep(0.5)
        self.removePids()

    def kill(self):
        '''Kills the environment without waiting.'''
        self.logging.info('SIGKILL received. Killing all processes.')
        myself = getpid()
        for pid in self.stopPid(self.pidfile):
            if pid != myself:
                self.sendSIGTERM(pid)
                while self.checkPidAlive(pid):
                    self.sendSIGKILL(pid)
        self.removePids()

    def sendSIGTERM(self, pid):
        '''Sends sigint signal to the pid.'''
        try:
            kill(int(pid),SIGTERM)
        except:
            pass
    
    def sendSIGKILL(self, pid):
        '''Sends sigkill signal to the pid.'''
        try:
            kill(int(pid),SIGKILL)
        except:
            pass

    def constructPidFileName(self,location,name):
        if location == None:
            return '/tmp/%s.pid'%name
        else:
            return location

    def startPid(self, pidfile):
        '''Handles the pid file logic in case we're starting.'''
        pids=[]
        try:
            pids = self.readPids(pidfile)
            if self.checkPids(pids):
                self.removePids()
                return True
        except Exception as err:
            if str(err).startswith('[Errno 2]'):
                return True
            else:
                print "The pid file exists but I can't process it.  Reason: %s"%(err)
                sys.exit(1)

    def stopPid(self, pidfile):
        '''Handles the pid file in case we're stopping.'''

        try:
            return self.readPids(pidfile)
        except Exception as err:
            print "I can't process the pidfile.  Reason: %s"%err
            sys.exit(1)

    def collectPids(self):
        '''Gets the pids of the current process and all the ones started by multiprocessing.'''

        pids = [getpid()]
        for process in self.processes:
            pids.append(process.pid)
        self.pids=pids
        return pids

    def checkPidAlive(self,pid):

        '''Returns True if the PID is still alive.'''
        try:
            kill(int(pid),0)
        except:
            return False
        else:
            return True

    def checkPids(self, pids):
        '''Reads the pids of the pidfile and sys.exit() if something goes wrong.

        returns True when all is fine.
         '''

        for pid in pids:
            if self.checkPidAlive(pid):
                print 'There is already a version of %s running with pid %s' % (self.name, pid)
                sys.exit(1)
            else:
                self.logging.warn ('Pidfile exists, but processes not running anymore.')
        return True

    def readPids(self,pidfile):
        '''Tries to open and read the pids from the pidfile

        Returns a list of pidfiles.'''

        f = open (pidfile,'r')
        pids = f.readlines()
        f.close()
        self.pids=pids
        return pids

    def writePids(self, pids):
        '''Writes all the pids into a pid file.

        The name of the file is set at __init__()  If no absolute filename is given server.pid is chosen in the current path.'''

        try:
            pidfile = open(self.pidfile,'w')
            pidfile.write("\n".join(map(str, pids)))
            pidfile.close()
            self.logging.debug('Pid file written to %s'%(self.pidfile))
        except Exception as err:
            self.logging.warn('Could not write pid file.  Reason: %s' %(err))
            sys.exit(1)

    def removePids(self):
        '''Deletes the PID file.'''

        try:
            remove(self.pidfile)
            self.logging.info('Pidfile removed.')
        except Exception as err:
            self.logging.warn('I could not remove the pidfile. Reason: %s'%(err))

    MAXFD = 2048
    def getMaximumFileDescriptors(self):
        """ Return the maximum number of open file descriptors for this process.

        Return the process hard resource limit of maximum number of
        open file descriptors. If the limit is “infinity”, a default
        value of ``MAXFD`` is returned.

        """
        limits = resource.getrlimit(resource.RLIMIT_NOFILE)
        result = limits[1]
        if result == resource.RLIM_INFINITY:
            result = MAXFD
        return result
