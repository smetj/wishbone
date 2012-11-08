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
from multiprocessing import Process
from time import sleep
from os import getpid, kill, remove, path
from signal import SIGINT
from logging import INFO
from wishbone.tools import configureLogging
from gevent import monkey;monkey.patch_all(thread=False)

class ParallelServer():
    '''Handles starting, stopping and daemonizing of one or multiple Wishbone instances.'''

    def __init__(self, instances=1, setup=None, daemonize=False, config=None, command=None, log_level=INFO, name='Server', pidfile=None):
        self.instances=instances
        self.setup=setup
        self.daemonize=daemonize
        self.config=config
        self.command=command
        self.log_level=log_level
        self.name=name
        self.wishbone=None
        self.processes=[]
        self.module_params={}
        self.logging = logging.getLogger( 'Server' )
        self.pidfile = self.constructPidFileName(pidfile,name)
        self.pids = None
        self.do()

    def do(self):
        '''Executes the command.'''
        if self.config != None:
            self.readConfig()
        if self.command == "debug" or (self.command == None and self.daemonize == False):
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
        for number in range(self.instances):
            if self.config == None:
                self.processes.append(Process(target=self.setup, name=number))
            else:
                self.processes.append(Process(target=self.setup, name=number, kwargs=self.module_params))
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

    def readConfig(self):
        '''Reads the config file.'''

        try:
            f = open (self.config,'r')
            self.module_params = json.load(f)
            f.close()
        except Exception as err:
            self.logging.critical('I could not read the config file. Reason: %s'%(err))
            self.module_params={}

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
