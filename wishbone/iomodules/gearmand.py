#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       gearmand.py
#
#       Copyright 2013 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

import logging
from wishbone.toolkit import QueueFunctions, Block
from gevent import Greenlet, spawn, sleep
from gevent.queue import Queue
from gearman import GearmanWorker
from Crypto.Cipher import AES
import base64
from gevent import monkey;monkey.patch_all()

class Gearmand(Greenlet, QueueFunctions, Block):
    '''
    ***Consumes jobs from a Gearmand server.***
    
    Consumes jobs from a Gearmand server.
    
    Parameters:
        * hostnames:    A list with hostname:port entries.
                        Default: []
                        Type: List

        * secret:   The AES encryption key to decrypt Mod_gearman messages.
                    Default: ''
                    Type: String

        * workers:  The number of gearman workers within 1 process.
                    Default: 1
                    Type: Int
    '''

    def __init__(self, name, *args, **kwargs):
        QueueFunctions.__init__(self)
        Greenlet.__init__(self)
        Block.__init__(self)
        self.logging = logging.getLogger( name )
        self.name = name
        self.logging.info ( 'Initiated' )
        self.hostnames=kwargs.get('hostnames',[])
        self.secret=kwargs.get('secret','')
        self.workers=kwargs.get('workers',1)
        self.cipher=AES.new(self.secret[0:32])
        self.worker_instances=[]
        self.background_instances=[]
        self.inbox=Queue(None)        
        
    def decode (self, gearman_worker, gearman_job):
        self.logging.debug ('Data received.')
        self.sendData({'header':{},'data':self.cipher.decrypt(base64.b64decode(gearman_job.data))}, queue='inbox')
        return "ok"

    def _run(self):
        self.logging.info('Started')
        for _ in range (self.workers):
            spawn(self.restartOnFailure)
        self.wait()

    def restartOnFailure(self):
        while self.block():
            try:
                self.worker_instances.append(GearmanWorker(self.hostnames))
                self.worker_instances[-1].register_task('perfdata', self.decode)
                self.worker_instances[-1].work()
            except Exception as err:
                self.logging.debug ('Connection to gearmand failed. Reason: %s'%err)               

    def shutdown(self):
        self.logging.info('Shutdown')
