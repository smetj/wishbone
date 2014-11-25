#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  emailout.py
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


from wishbone import Actor
from gevent import monkey; monkey.patch_socket()
from email.mime.text import MIMEText
import smtplib


class EmailOut(Actor):

    '''**Sends out incoming events as email.**

    Treats event.data as the body of an email.

    The event.header.<self.name> is supposed to have following keys:
        - subject(str)
        - from(str)
        - to(list)


    Parameters:

        - mta(string)("localhost:25)
           |  The address:port of the MTA to submit the
           |  mail to.

        - namespace(string)(None)
           |  The header namespace containing the address information.


    Queues:

        - inbox
           |  Incoming messages

    '''

    def __init__(self, actor_config, mta="localhost:25", namespace=None):
        Actor.__init__(self, actor_config)

        self.mta = mta

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        if namespace is None:
            self.namespace = self.name
        else:
            self.namespace = namespace

    def consume(self, event):

        if not event.header.hasNamespace(self.namespace):
            self.logging.error("Event received without <%s> header namespace. Purged" % (self.namespace))
            raise Exception("Event received without <%s> header namespace. Purged" % (self.namespace))

        for item in ["from", "to", "subject"]:
            if not event.hasHeaderKey(self.namespace, item):
                self.logging.error("Event received without <%s> header key. Purged" % (item))
                raise Exception("Event received without <%s> header key. Purged" % (item))

        if not isinstance(event.getHeaderValue(self.namespace, "to"), list):
            self.logging.error("the \"to\" header key should be of type list.")
            raise Exception("the \"to\" header key should be of type list.")

        try:
            message = MIMEText(str(event.data))
            message["Subject"] = event.getHeaderValue(self.namespace, "subject")
            message["From"] = event.getHeaderValue(self.namespace, "from")
            message["To"] = ",".join(event.getHeaderValue(self.namespace, "to"))

            mta = smtplib.SMTP(self.mta)
            mta.sendmail(event.getHeaderValue(self.namespace, "from"),
                         event.getHeaderValue(self.namespace, "to"),
                         message.as_string()
                         )
        except Exception as err:
            self.logging.error("Failed to send out email.  Reason: %s" % (err))
            raise