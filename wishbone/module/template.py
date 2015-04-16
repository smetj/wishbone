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

        - location(str)("./")
           |  The directory containing templates.

        - template(str)()*
           |  The template filename stored in directory <location>.

        - header_templates(list)([])*
           |  An optional list of strings with header references
           | containing templates.
           | <module_instance>.header.<key>



    Queues:

        - inbox
           |  Incoming events

        - outbox
           |  Outgoing events

    '''

    def __init__(self, actor_config, location="./", template=None, header_templates=[]):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        if self.kwargs.template is not None:
            self.kwargs.templates = Environment(loader=FileSystemLoader(self.kwargs.location))

    def consume(self, event):
        event = self.construct(event)
        self.submit(event, self.pool.queue.outbox)

    def construct(self, event):

        for template_ref in self.kwargs.header_templates:
            try:
                (namespace, part, variable) = template_ref.split('.')
                template = event.getHeaderValue(namespace, variable)
                template_r = JinjaTemplate(template)
                event.setHeaderValue(variable, template_r.render(**event.data), namespace)
            except Exception as err:
                self.logging.warning(
                    "Failed to convert header key '%s'.  Reason: %s" % (variable, err))
                raise

        if self.kwargs.template is not None:
            try:
                template = self.kwargs.templates.get_template(self.kwargs.template)
            except Exception as err:
                self.logging.error('No template found with filename "%s%s".' % (self.kwargs.location, self.kwargs.template))
                raise
            else:
                try:
                    event.data = template.render(**event.data)
                except Exception as err:
                    self.logging.error('There was an error processing the template. Reason: %s' % (err))
                    raise
        return event
