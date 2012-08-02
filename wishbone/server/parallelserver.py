#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  parallelserver.py
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

import logging
import daemon
from multiprocessing import Process, Event
from time import sleep
from os import getpid, kill, remove, path
from signal import SIGINT
import sys
from gevent import monkey
from wishbone.tools import configureLogging 

class ParallelServer():
    '''Handles starting, stopping and daemonizing of one or multiple Wishbone instances.''' 
    
    def __init__(self, instances=1, setup=None, daemonize=False, log_level=logging.INFO, name='Server'):
        self.instances=instances
        self.setup=setup
        self.daemonize=daemonize
        self.log_level=log_level
        self.name=name
        self.pidfile='/tmp/%s.pid'%name
        self.wishbone=None
        self.processes=[]
        self.pids = []
    
    def start(self):
        '''Starts the server environment in fore- or background.'''
                
        if self.checkPids() == True:
            if self.daemonize == True:
                print 'Starting %s in background.' % (self.name)
                configureLogging(name=self.name, syslog=True, loglevel=self.log_level)
                self.logging = logging.getLogger( 'Server' )
                with daemon.DaemonContext():
                    self.__start()
            else:
                monkey.patch_all()
                configureLogging(loglevel=self.log_level)
                self.logging = logging.getLogger( 'Server' )
                self.__start()
    
    def __start(self):
        '''Actually starts the environment.  Should only be called by self.start().'''
        
        for number in range(self.instances):
            self.processes.append(Process(target=self.setup, name=number))
            self.processes[number].start()
            self.logging.info('Instance #%s started.'%number)
        
        self.pids = self.collectPids()
        self.writePids()
        self.logging.info('Started with pids: %s' % ', '.join(map(str, self.pids)))
        
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        '''Stops the environment.'''
        
        self.logging.info('SIGINT received. Stopping processes.  Send SIGINT again to stop everything without waiting.')
        for process in self.processes:
            self.logging.info('Waiting for %s' %process.name)
            try:
                process.join()
            except KeyboardInterrupt:
                #some people have no patience
                process.terminate()
        self.removePids()
        logging.shutdown()

    @staticmethod
    def sendSIGINT(pidfile):
        '''Sends sigint signal to the pids.
        
        Needs to be a static method to facilitate init scripts.'''
        for pid in Server.readPids(pidfile):
            kill(int(pid),SIGINT)
        print "Tail the logfile to see progress."

    @staticmethod    
    def readPids(pidfile):
        '''Tries to open and read the pids from the pidfile
        
        Returns a list of pidfiles.'''

        pids=[]
        
        if path.exists(pidfile):
            try:
                pidfile = open (pidfile,'r')
            except Exception as err:
                print ('Pidfile exists, but I could not read it.  Reason: %s' % err)
                sys.exit(1)
            else:
                for pid in pidfile.readlines():
                    pids.append(pid)
                pidfile.close()

        return pids

    def collectPids(self):
        '''Gets the pids of the current process and all the ones started by multiprocessing.'''
        
        pids = [getpid()]
        for process in self.processes:
            pids.append(process.pid)
        return pids
    
    def checkPids(self):
        '''Reads the pids of the pidfile and sys.exit() if something goes wrong.
        
        returns True when all is fine.
         '''
        
        pids = self.readPids(self.pidfile)
        for pid in pids:
            try:
                kill(int(pid),0)
            except:
                pass
            else:
                print 'There is already a version of %s running with pid %s' % (self.name, pid)
                sys.exit(1)
            
            try:
                remove(self.pidfile)
                print 'Pidfile exists, but processes not running anymore. Removed.'
                return True
            except Exception as err:
                print 'Pidfile exists, but I could not remove it.  Reason: %s' % (err)
                sys.exit(1)
        return True

    def writePids(self):
        '''Writes all the pids into a pid file.
        
        The name of the file is set at __init__()  If no absolute filename is given server.pid is chosen in the current path.'''
        
        try:
            pidfile = open(self.pidfile,'w')
            pidfile.write("\n".join(map(str, self.pids)))
            pidfile.close()
        except Exception as err:
            self.logging.warn('Could not write pid file.  Reason: %s' %(err))
            
    def removePids(self):
        '''Deletes the PID file.'''
        
        try:
            remove(self.pidfile)
            self.logging.info('Pidfile removed.')
        except Exception as err:
            self.logging.warn('I could not remove the pidfile. Reason: '%(err))            
