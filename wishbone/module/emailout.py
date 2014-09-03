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
from gevent import sleep
import smtplib


class EmailOut(Actor):

    '''**Sends out incoming events as email.**

    Treats event["data"] as the body of an email.

    The event["header"][self.name] is supposed to have following keys:
        - subject(str)
        - from(str)
        - to(list)


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - mta(string)("localhost:25)
           |  The address:port of the MTA to submit the
           |  mail to.

        - key(string)(None)
           |  The header key containing the address information.


    Queues:

        - inbox
           |  Incoming messages

    '''

    def __init__(self, name, size, frequency, mta="localhost:25", key=None):

        Actor.__init__(self, name)
        self.name = name
        self.mta = mta

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        if key is None:
            self.key = self.name
        else:
            self.key = key

    def consume(self, event):

        if self.key not in event["header"]:
            self.logging.error("Event received without <%s> header key. Purged" % (self.key))
            raise Exception("Event received without <%s> header key. Purged" % (self.key))

        for item in ["from", "to", "subject"]:
            if item not in event["header"][self.key]:
                self.logging.error("Event received without <%s> header key. Purged" % (item))
                raise Exception("Event received without <%s> header key. Purged" % (item))

        if not isinstance(event["header"][self.key]["to"], list):
            self.logging.error("the \"to\" header key should be of type list.")
            raise Exception("the \"to\" header key should be of type list.")

        try:
            message = msg = MIMEText(str(event["data"]))
            message["Subject"] = event["header"][self.key]["subject"]
            message["From"] = event["header"][self.key]["from"]
            message["To"] = ",".join(event["header"][self.key]["to"])

            mta = smtplib.SMTP(self.mta)
            mta.sendmail(event["header"][self.key]["from"],
                         event["header"][self.key]["to"],
                         message.as_string()
                         )
        except Exception as err:
            self.logging.error("Failed to send out email.  Reason: %s" % (err))
            raise