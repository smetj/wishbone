#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  emailout.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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


from wishbone import Actor
from wishbone.event import Bulk
from gevent import monkey; monkey.patch_socket()
from email.mime.text import MIMEText
import smtplib


class EmailOut(Actor):

    '''**Sends out incoming events as email.**

    Treats event.data as the body of an email.


    Parameters:

        - selection(str)("@data")
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.

        - mta(string)("localhost:25)
           |  The address:port of the MTA to submit the
           |  mail to.

        - to(list)([])*
           |  A list of destinations.

        - subject(str)("Wishbone")*
           |  The subject of the email.

        - from_address(str)("wishbone@localhost")*
           |  The form email address.


    Queues:

        - inbox
           |  Incoming messages

    '''

    def __init__(self, actor_config, selection="@data", mta="localhost:25", subject="Wishbone", to=None, from_address=None):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        if isinstance(event, Bulk):
            data = event.dumpFieldAsString(self.kwargs.selection)
        else:
            data = str(event.get(self.kwargs.selection))

        try:
            message = MIMEText(data)
            message["Subject"] = self.kwargs.subject
            message["From"] = self.kwargs.from_address
            message["To"] = ",".join(self.kwargs.to)

            mta = smtplib.SMTP(self.kwargs.mta)
            mta.sendmail(self.kwargs.from_address,
                         self.kwargs.to,
                         message.as_string()
                         )
        except Exception as err:
            raise Exception("Failed to send out email.  Reason: %s" % (err))
