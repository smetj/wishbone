#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wb_inotify.py
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

from wishbone.module import InputModule

# I know no other working way to actually monkey patch select
# when inotify is imported.
# If you know another way, please consider submitting a
# patch or merge request
# todo(smetj): Fix dirty monkey patch of inotify select
import sys
from gevent import monkey; monkey.patch_all()
sys.modules["select"] = sys.modules["gevent.select"]
sys.modules["select"].epoll = sys.modules["select"].poll

from inotify.adapters import Inotify
from inotify import constants

from gevent import sleep
import os
import fnmatch


class WBInotify(InputModule):

    '''**Monitors one or more paths for inotify events.**

    Monitors one or more paths for the defined inotify events.

    Inotify events can have following values:

        - IN_ACCESS
        - IN_ALL_EVENTS
        - IN_ATTRIB
        - IN_CLOEXEC
        - IN_CLOSE
        - IN_CLOSE_NOWRITE
        - IN_CLOSE_WRITE
        - IN_CREATE
        - IN_DELETE
        - IN_DELETE_SELF
        - IN_DONT_FOLLOW
        - IN_IGNORED
        - IN_ISDIR
        - IN_MASK_ADD
        - IN_MODIFY
        - IN_MOVE
        - IN_MOVED_FROM
        - IN_MOVED_TO
        - IN_MOVE_SELF
        - IN_NONBLOCK
        - IN_ONESHOT
        - IN_ONLYDIR
        - IN_OPEN
        - IN_Q_OVERFLOW
        - IN_UNMOUNT


    Outgoing events have following format::

        {"path": "/tmp/test", "inotify_type": "IN_ACCESS"}


    Parameters::

        - destination(str)(data)
           |  In which field to store the inotify event data.

        - native_event(bool)(False)
           |  Whether to expect incoming events to be native Wishbone events.

        - initial_listing(bool)(True)

           |  When True, generates for each defined path an event.  This is
           |  useful to initially give depending modules the filenames they
           |  need to function.

        - glob_pattern(str)(*)

           |  A glob pattern to filter out only matching files.

        - paths(dict)({"/tmp": ["IN_CREATE", "IN_CLOSE_WRITE"]})

           |  A dict of paths with a list of inotify events to monitor.  When
           |  the list is empty no filtering is done and results into all
           |  inotify events going through.


    Queues::

        - outbox
           |  Outgoing notify events.

    '''

    def __init__(self, actor_config, native_event=False, destination="data",
                 initial_listing=True, glob_pattern="*", paths={"/tmp": ["IN_CREATE", "IN_CLOSE_WRITE"]}):
        InputModule.__init__(self, actor_config)

        self.pool.createQueue("outbox")

    def preHook(self):

        for path, event_types in self.kwargs.paths.items():
            for event_type in event_types:
                if event_type not in constants.__dict__:
                    raise Exception("Inotify event type '%s' defined for path '%s' is not valid." % (event_type, path))

        for path, inotify_types in self.kwargs.paths.items():
            self.sendToBackground(self.monitor, path, inotify_types, self.kwargs.glob_pattern)

    def monitor(self, path, inotify_types, glob_pattern):
        '''Monitors ``path`` for ``inotify_types`` on files and dirs matching ``glob_pattern``

        :param str path: The path to monitor
        :param list inotify_types: A list of inotify types to monitor
        :param str glob_pattern: Paths need to match in order to be returned.
        :return: None
        '''

        all_types = ', '.join(inotify_types)
        if all_types == '':
            all_types = "ALL"

        while self.loop():
            if os.path.exists(path) and os.access(path, os.R_OK):
                self.logging.info("Started to monitor path '%s' for '%s' inotify events on paths matching '%s'." % (os.path.abspath(path), all_types, glob_pattern))

                if self.kwargs.initial_listing:
                    for p in self.__getAllFiles(path, glob_pattern):
                        for payload in self.decode(p):
                            event = self.generateEvent({"path": os.path.abspath(payload), "inotify_type": "WISHBONE_INIT"}, self.kwargs.destination)
                            self.submit(event, "outbox")
                try:
                    for abs_path, i_type in self.__setupInotifyMonitor(path, inotify_types, glob_pattern):
                        for payload in self.decode(abs_path):
                            event = self.generateEvent({"path": payload, "inotify_type": i_type}, self.kwargs.destination)
                            self.submit(event, "outbox")
                except Exception as err:
                    self.logging.critical('Failed to initialize inotify monitor. This needs immediate attention. Reason: %s' % err)
                    sleep(1)
            else:
                self.logging.warning("The defined path '%s' does not exist or is not readable. Will sleep for 5 seconds and try again." % (path))
                sleep(5)

    def __getAllFiles(self, path, glob_pattern):

        """
        Returns all files it can find in ``path``.  If ``path`` is a directory
        it returns all files found in the directory (not recursive)

        :param str path: The path to investigate.
        :param str glob_pattern: The patterns to which files and dirs have to match.
        :return: Generator
        """

        if os.path.isdir(path):
            all_files = [os.path.abspath("%s/%s" % (path, name)) for name in os.listdir(path) if os.path.isfile("%s/%s" % (path, name))]
        else:
            all_files = [os.path.abspath(path)]

        for f in all_files:
            if fnmatch.fnmatch(f, glob_pattern):
                yield f

    def __setupInotifyMonitor(self, path, inotify_types, glob_pattern):

        '''

        Initializes an inotify monitor process on ``path`` and yields the
        defined ``inotify_types`` generated on the paths matching the
        ``glob_pattern``.

        :param str path: The path to monitor
        :param list inotify_types: A list of inotify types to monitor
        :param str glob_pattern: Paths need to match in order to be returned.
        :return: generator

        '''

        file_exists = True
        i = Inotify()
        i.add_watch(path)

        while file_exists and self.loop():
            for event in i.event_gen(yield_nones=False):
                if event is not None:
                    for inotify_type in event[1]:
                        if inotify_type in inotify_types or inotify_types == []:
                            abs_path = os.path.abspath("%s/%s" % (event[2], event[3]))
                            if fnmatch.fnmatch(abs_path, glob_pattern):
                                yield abs_path.rstrip('/'), inotify_type
                        if inotify_type == "IN_DELETE_SELF":
                            file_exists = False
                            break
                else:
                    sleep(1)
