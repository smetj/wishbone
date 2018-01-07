#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  template.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
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
from wishbone.module import ProcessModule
from os.path import isabs


class Template(ProcessModule):

    '''**Renders Jinja2 templates.**

    Renders Jinja2 templates using the event content as context. Templates can
    be read from a file or directly from the bootstrap file.


    Parameters::

        - filename(str)(None)*
           |  The absolute template filename to load.
           |  Can be a dynamic lookup. Assing None
           |  (default) to disable.

        - destination(str)(data)*
           |  The key to store the rendered file template.


        - templates(dict)({})*
           |  A dict of templates to render. The dict keys are the fields to
           |  assign the rendered string to.


    Queues::

        - inbox
           |  Incoming events

        - outbox
           |  Outgoing events

    '''

    def __init__(self, actor_config, filename=None, destination="data", templates={}):
        ProcessModule.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")

        self.__template_loaders = {}

        if self.kwargs.filename is not None:
            self.file_template = Environment(loader=FileSystemLoader(self.kwargs.filename))

    def consume(self, event):

        for key, result in event.kwargs.templates.items():
            event.set(result, key)

        if event.kwargs.filename is not None:

            if isabs(event.kwargs.filename):
                data = self.renderFile(event.kwargs.filename, event.dump())
                event.set(data, event.kwargs.destination)
            else:
                self.logging.error("%s is not an absolute path. Skipped" % (event.kwargs.filename))

        self.submit(event, "outbox")

    def renderFile(self, filename, data):

        # TODO(smetj): calling thie private function is ugly, rewrite this part.
        return self._Actor__renderKwargs.env_template.get_template(filename).render(data)
