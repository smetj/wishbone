#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  server.py
#
#  Copyright 2012 Jelle Smet development@smetj.net
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
import logging
import json
import sys
import resource
import argparse
from multiprocessing import Process
from time import sleep
from os import getpid, kill, remove, path
from signal import SIGINT
from logging import INFO, DEBUG
from wishbone.tools import configureLogging
from wishbone import Wishbone
from gevent import monkey;monkey.patch_all(thread=False)

class BootStrap():
    '''Bootstraps a Wishbone setup using the received configuration.'''
    
    def __init__(self,name="WishBone"):
        
        self.name=name
        cli=self.parseArguments()
        conf=self.readConfig(cli["config"])
        log_level = self.translateLogLevel(cli["loglevel"])
        ParallelServer( instances=int(cli['instances']),
                    setup=WishbBoneSkeleton,
                    setup_args=[conf],
                    command=cli['command'][0],
                    name=name,
                    log_level=log_level
        )
    
    def parseArguments(self):
        
        parser = argparse.ArgumentParser()
        parser.add_argument('command', nargs=1, help='Which command to issue.  start, stop, status or debug.')
        parser.add_argument('--config', dest='config', help='The location of the configuration file.')
        parser.add_argument('--instances', dest='instances', default=1, help='The number of parallel instances to start.')
        parser.add_argument('--loglevel', dest='loglevel', default="info", help='The loglevel you want to use. [info,warn,crit,debug]')
        parser.add_argument('--pid', dest='pid', default=1, help='The absolute path of the pidfile.')
        return vars(parser.parse_args())
    
    def readConfig(self,filename):
        try:
            f = open(filename, "r")
            config = f.readlines()
            f.close()
            return json.loads(''.join(config))
        except Exception as err:
            print ('An error occurred when processing the config files. Reason: %s'%err)
            sys.exit(1)
    
    def translateLogLevel(self,loglevel):
        if loglevel == "debug":
            return DEBUG
        elif loglevel == "info":
            return INFO
        
class WishbBoneSkeleton():
    '''A skeleton class which initializes and connects the WishBone modules according to the bootstrap configuration.'''
    
    def __init__(self, conf):
        self.conf=conf
        self.wb = self.setup()
        self.wb.start()

    def setup(self):
        wb = Wishbone()
        for module in self.conf["bootstrap"]:
            wb.registerModule ( (self.conf["bootstrap"][module]["module"],self.conf["bootstrap"][module]["class"],module),
                                **self.conf["bootstrap"][module]["variables"]
            )    
        for source in self.conf["routingtable"]:
            for destination in self.conf["routingtable"][source]:
                (src_class,src_queue)=source.split('.')
                (dst_class,dst_queue)=destination.split('.')
                src_instance=getattr(wb,src_class)
                dst_instance=getattr(wb,dst_class)
                wb.connect(getattr(src_instance,src_queue),getattr(dst_instance,dst_queue))
        return wb

class ParallelServer():
    '''Handles starting, stopping and daemonizing of one or multiple Wishbone instances.
    
    Parameters:
    
        * instances:        The number of parallel instances to start.
        * setup:            The class containing the WishBone setup.
        * setup_args:       *args to initiate the setup class.        
        * setup_kwargs:     **kwargs to initiate the setup class.
        * daemonize:        Detach into background or not.
        * command:          Which command to invoke. (start, debug, stop, status)
        * log_level:        The loglevel to use
        * server:           The name of this insance.
        * pidfile:          The absolute pathname of the pidfile.    
    '''

    def __init__(self, instances=1, setup=None, setup_args=None, setup_kwargs={}, command=None, log_level=INFO, name='Server', pidfile=None):
        self.instances=instances
        self.setup=setup
        self.setup_kwargs=setup_kwargs
        self.setup_args=setup_args
        self.command=command
        self.log_level=log_level
        self.name=name
        self.wishbone=None
        self.processes=[]
        self.logging = logging.getLogger( 'Server' )
        self.pidfile = self.constructPidFileName(pidfile,name)
        self.pids = None
        self.do()

    def do(self):
        '''Executes the command.'''
        if self.command == "debug":
            configureLogging(loglevel=self.log_level)
            self.debug()
        elif self.command == "start":
            self.handle=configureLogging(syslog=True,loglevel=self.log_level,get_handle=True)
            self.start()
        elif self.command == "stop":
            configureLogging(syslog=False,loglevel=self.log_level)
            self.stop()
        elif self.command == 'kill':
            configureLogging(syslog=True,loglevel=self.log_level)
            self.kill()

    def debug(self):
        '''Starts the server environment in the foreground.'''
        if self.startPid(self.pidfile):
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
        
        self.logging.info('Starting %s in foreground.' % (self.name))
        for number in range(int(self.instances)):
            self.processes.append(Process(target=self.setup, name=number, args=self.setup_args, kwargs=self.setup_kwargs))
            #if self.setup_config == None:
                #self.processes.append(Process(target=self.setup, name=number))
            #else:
                #self.processes.append(Process(target=self.setup, name=number, args=self.setup_args, kwargs=self.setup_kwargs))
            self.processes[number].start()
            self.logging.info('Instance #%s started.'%number)

        self.writePids(self.collectPids())
        self.logging.info('Started with pids: %s' % ', '.join(map(str, self.pids)))
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            for process in self.processes:
                process.join()
        self.removePids()

    def stop(self):
        '''Stops the environment.'''
        self.logging.info('SIGINT received. Stopping processes.  Send SIGINT again to stop everything without waiting.')        
        
        
        for pid in self.stopPid(self.pidfile):
            self.sendSIGINT(pid)
        for pid in self.pids:
            while self.checkPidAlive(pid):
                sleep(1)
        self.removePids()

    def kill(self):
        '''Kills the environment.'''
        pass
    
    def sendSIGINT(self, pid):
        '''Sends sigint signal to the pid.'''

        kill(int(pid),SIGINT)

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
