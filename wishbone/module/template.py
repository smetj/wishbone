#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# template.py
#
#  Copyright 2013 Jelle Smet <jelle.smet@tomtom.com>
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

from jinja2 import Environment, FileSystemLoader
from jinja2 import Template as JinjaTemplate
from wishbone import Actor


class Template(Actor):

    '''**A Wishbone module which generates a text from a dictionary and a template.**

    Convert a dictionary to a text using the Jinja2 template defined in the
    header.

    Optionally header template values can be converted too.


    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - location(str)("./")
           |  The directory containing templates.

        - key(str)(self.name)
           |  The header key storing configuration.

        - header_templates(list)([])
           |  An optional list of keys containing templates.



    Queues:

        - inbox
           |  Incoming events

        - outbox
           |  Outgoing events

    '''

    def __init__(self, name, size, frequency, location="./", key=None, header_templates=[]):
        Actor.__init__(self, name, size, frequency)

        self.location = location
        if key is None:
            self.key = self.name
        else:
            self.key = key

        self.header_templates = header_templates
        self.templates = Environment(loader=FileSystemLoader(location))

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):
        event = self.construct(event)
        self.submit(event, self.pool.queue.outbox)

    def construct(self, event):

        try:
            event["header"][self.key]["template"]
        except KeyError:
            self.logging.error(
                'Header information event["header"]["%s"]["template"] was expected but not found. Event purged.' % (self.key))
            raise

        for key in self.header_templates:
            try:
                template = JinjaTemplate(event["header"][self.key][key])
                event["header"][self.key][key] = template.render(**event["data"])
            except Exception as err:
                self.logging.warning(
                    "Failed to convert header key %s.  Reason: %s" % (key))
                raise

        try:
            template = self.templates.get_template(event["header"][self.key]["template"])
        except Exception as err:
            self.logging.error("Template %s does not exist as a file in directory %s." % (event["header"][self.key]["template"], self.location))
            raise
        else:
            try:
                event["data"] = template.render(**event["data"])
            except Exception as err:
                self.logging.error('There was an error processing the template. Reason: %s' % (err))
                raise
        return event
