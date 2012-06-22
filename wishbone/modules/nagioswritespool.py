#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       nagioswritespool.py
#       
#       Copyright 2012 Jelle Smet development@smetj.net
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

from wishbone.toolkit import PrimitiveActor
from tempfile import mkstemp
from os import write, close, rename
from time import time


class NagiosSpoolWriter(PrimitiveActor):
    '''A class which takes LogStash processed Nagios logs and writes them to the Nagios spool file.

    You can use other data sources than LogStash however, as long as you keep the expected data structure.
    The grok rules we're talking about are: https://github.com/jordansissel/grok/blob/master/patterns/nagios
    
    Services:
    {"@fields":{    nagios_type:"External Command",
                    nagios_command:"PROCESS_SERVICE_CHECK_RESULT",
                    nagios_hostname:"host_name",
                    nagios_service:"service_description",
                    nagios_state:"return_code",
                    nagios_check_result:"plugin_output"}
                    }
    
    Hosts:
    {"@fields":{    nagios_type:"External Command",
                    nagios_command:"PROCESS_HOST_CHECK_RESULT",
                    nagios_hostname:"host_name",
                    nagios_state:"return_code",
                    nagios_check_result:"plugin_output"}
                    }
                    
    Parameters:
        * check_results_dir: The Nagios spool directory to which results should be written.
        
    '''
    
    def __init__(self, name, *args, **kwargs):
        PrimitiveActor.__init__(self, name)
        self.check_results_dir = kwargs.get('check_results_dir','./')
    
    def consume(self,doc):
        file = mkstemp(prefix="check", dir=self.check_results_dir)
        write(file[0], self.__format(doc['data']))
        close(file[0])
        #rename file
        rename (file[1],file[1]+'.ok')
           
               
    def __formatCheck(self, data):
        if data['@fields']['nagios_command'] == 'PROCESS_SERVICE_CHECK_RESULT':
            return ( '### NagSpoolWriter ###\nstart_time=%d.*\nhost_name=%s\nservice_description=%s\ncheck_type=1\nearly_timeout=1\nexited_ok=1\nreturn_code=%d\noutput=%s\\n\n'%(time(),data['@fields']['nagios_hostname'],data['@fields']['nagios_service'],data['@fields']['nagios_state'],data['@fields']['nagios_check_result']))
        else:
            return ( '### NagSpoolWriter ###\nstart_time=%d.*\nhost_name=%s\ncheck_type=1\nearly_timeout=1\nexited_ok=1\nreturn_code=%d\noutput=%s\\n\n'%(time(),data['@fields']['nagios_hostname'],data['@fields']['nagios_state'],data['@fields']['nagios_check_result']))        
    
    def shutdown(self):
        self.logging.info('Shutdown')
