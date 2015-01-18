#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  emailout.py
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


from wishbone import Actor
from gevent import monkey; monkey.patch_socket()
from email.mime.text import MIMEText
import smtplib


class EmailOut(Actor):

    '''**Sends out incoming events as email.**

    Treats event.data as the body of an email.


    Parameters:

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

    def __init__(self, actor_config, mta="localhost:25", subject="Wishbone", to=None, from_address=None):
        Actor.__init__(self, actor_config, ["to", "from_address", "subject"])
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        try:
            message = MIMEText(str(event.data))
            message["Subject"] = self.subject
            message["From"] = self.from_address
            message["To"] = ",".join(self.to)

            mta = smtplib.SMTP(self.mta)
            mta.sendmail(self.from_address,
                         self.to,
                         message.as_string()
                         )
        except Exception as err:
            self.logging.error("Failed to send out email.  Reason: %s" % (err))
            raise