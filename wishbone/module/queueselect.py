#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  queueselect.py
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

from wishbone.module import ProcessModule
from wishbone.utils.structured_data_file import StructuredDataFile
from wishbone.error import InvalidData


class QueueSelect(ProcessModule):

    '''**Submits message to the queue defined by a rendered template.**

    Renders a list of templates against the event.  Events are submitted to
    the queue a rendered template returns.

    Typically this module is used to route messages using Jinja2 conditionals
    and logic.

    A rule rule looks like this:

    ::

        { "name": "name of the rule",
          "queue": "{{ 'queue_1,queue_one' if data.one == 1 else 'queue_2,queue_two' }}"
          "payload":
            "queue_1": {
                "detail_1": "some value",
                "detail_2": "some other value",
            },
            "queue_2": {
                "detail_1": "some value",
                "detail_2": "some other value",
            }
          }
        }


    The <file> queue expects events containing the absolute path of a YAML
    file to read (or delete). Typically this queue receives events from
    wishbone.module.input.inotify.

    Events of type "IN_CREATE", "IN_CLOSE_WRITE", "IN_DELETE", "WISHBONE_INIT"
    are processed all others are ignored.


    Parameters::

        - templates(list)([])*
           |  A list consisting out of template dicts as explained above.

        - log_matching(bool)(False)
           |  Whether to produce debug log messages for matches.
           | Can be verbose hence it's configurable.


    Queues::

        - inbox
           |  Incoming events

        - outbox
           |  Outgoing events

        - nomatch
           |  Events not matching at least 1 rule.

        - file
           |  Read rules from YAML file or delete them.

    '''

    INOTIFY_TYPES = [
        "IN_CREATE",
        "IN_CLOSE_WRITE",
        "IN_DELETE",
        "WISHBONE_INIT"
    ]

    def __init__(self, actor_config, templates=[], log_matching=False):
        ProcessModule.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.pool.createQueue("file")
        self.pool.createQueue("nomatch")

        self.registerConsumer(self.consume, "inbox")
        self.registerConsumer(self.handleFileTemplate, "file")

        self.template_loader = StructuredDataFile(
            expect_json=False,
            expect_yaml=True
        )

    def consume(self, event):

        for template in event.kwargs.templates:
            self.handleQueueSelect(
                template_name=template.name,
                queue_list=template.queue,
                payload=template.get("payload", {}),
                event=event)

        for file_name, file_content in self.template_loader.dump().items():
            try:
                queue_name = event.render(file_content["queue"])
            except InvalidData as err:
                self.logging.error("Failed to render template '%s'. Reason: %s" % (err))
            else:
                self.handleQueueSelect(
                    template_name=file_name,
                    queue_list=queue_name,
                    payload=file_content["payload"].get(queue_name, {}),
                    event=event)

    def handleQueueSelect(self, template_name, queue_list, payload, event):
        '''Handles submitting <event> into queue <queue_name>.'''

        for queue_name in [queue.strip() for queue in queue_list.split(',')]:

            if self.pool.hasQueue(queue_name):

                if self.kwargs.log_matching:
                    self.logging.debug("Template '{template_name}' selected queue '{queue_name}' to route event '{event_id}' to.".format(
                        template_name=template_name,
                        queue_name=queue_name,
                        event_id=event.get('uuid')
                    ))

                # Construct and set the payload
                queue_payload = {
                    "original_event_id": event.get('uuid'),
                    "queue": queue_name,
                    "payload": payload
                }
                e = event.clone()
                e.set(queue_payload, "tmp.%s" % (self.name))

                # Submit a clone of the event to the required queue
                self.submit(e, queue_name)

            else:
                if self.kwargs.log_matching:
                    self.logging.debug("Template '{template_name}' selected non-existing queue '{queue_name}' to route event '{event_id}' to.".format(
                        template_name=template_name,
                        queue_name=queue_name,
                        event_id=event.get('uuid')
                    ))
                self.submit(event, "nomatch")

    def handleFileTemplate(self, event):
        '''Loads or deletes the template file defined in data.path.'''

        inotify_type = event.get("data.inotify_type")
        path = event.get("data.path")

        if inotify_type in self.INOTIFY_TYPES:
            if inotify_type == "IN_DELETE":
                self.template_loader.delete(path)
                self.logging.debug("Removed template file '{path}' from cache.".format(path=path))
            else:
                self.template_loader.load(path)
                self.logging.debug("Loaded template file '{path}'".format(path=path))
        else:
            self.logging.warning("No support for inotify type '{inotify_type}'. Dropped.".format(
                inotify_type=inotify_type
            ))
