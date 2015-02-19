#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  match.py
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
from gevent import spawn, sleep
from .matchrules import MatchRules
from .readrules import ReadRulesDisk
import os
from copy import deepcopy


class Match(Actor):

    '''**Pattern matching on a key/value document stream.**

    This module routes messages to a queue associated to the matching rule
    set.  The event['data'] payload has to be of <type 'dict'>.  Typically,
    the source data is JSON converted to a Python dictionary.

    The match rules can be either stored on disk or directly defined into the
    bootstrap file.


    A match rule is written in YAML syntax and consists out of 2 parts:

        - condition:

        A list of dictionaries holding with the individual conditions which
        ALL have to match for the complete rule to match.

        re:     Regex matching
        !re:    Negative regex matching
        >:      Bigger than
        >=:     Bigger or equal than
        <:      Smaller than
        <=:     Smaller or equal than
        =:      Equal than
        in:     Evaluate list membership

        - queue:

        The queue section contains a list of dictionaries/maps each containing
        1 key with another dictionary/map as a value.  These key/value pairs
        are added to the *header section* of the event and stored under the
        queue name key.
        If you are not interested in adding any information to the header you
        can leave the dictionary empty.  So this would be valid:

    All rules will be evaluated sequentially in no particular order.  When a
    rule matches, evaluation the other rules will continue untill all rules
    are processed.

    Examples
    ~~~~~~~~

    This example would route the events - with field "greeting" containing
    the value "hello" - to the outbox queue without adding any information
    to the header of the event itself.

    ::

        condition:
            - greeting: re:^hello$

        queue:
            - outbox:



    This example combines multiple conditions and stores 4 variables under
    event["header"][self.name] while submitting the event to the modules'
    **email** queue.

    ::

        condition:
            - check_command: re:check:host.alive
            - hostproblemid: re:\d*
            - hostgroupnames: in:tag:development

        queue:
            - email:
                from: monitoring@yourdomain.com
                to:
                    - oncall@yourdomain.com
                subject: UMI - Host  {{ hostname }} is  {{ hoststate }}.
                template: host_email_alert



    Parameters:

        - name(str)
           |  The name of the module.

        - size(int)
           |  The default max length of each queue.

        - frequency(int)
           |  The frequency in seconds to generate metrics.

        - location(str)(None)
           |  The directory containing rules.
           |  If none, no rules are read from disk.

        - rules(list)({})
           |  A list of rules in the above described format.


    Queues:

        - inbox
           |  Incoming events

        - <queue_name>
           |  The queue which matches a rule.

    '''

    def __init__(self, name, size=100, frequency=1, location=None, rules={}):
        Actor.__init__(self, name, size, frequency)
        self.location = location
        self.rules = rules
        self.__active_rules = {}
        self.match = MatchRules()
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        self.createDir()
        self.__active_rules = self.rules
        if self.location is not None:
            self.logging.info("Rules directoy '%s' defined." % (self.location))
            spawn(self.getRules)

    def createDir(self):

        if os.path.exists(self.location):
            if not os.path.isdir(self.location):
                raise Exception("%s exists but is not a directory" % (self.location))
            else:
                self.logging.info("Directory %s exists so I'm using it." % (self.location))
        else:
            self.logging.info("Directory %s does not exist so I'm creating it." % (self.location))
            os.makedirs(self.location)

    def getRules(self):

        self.logging.info("Monitoring directory '%s' for changes" % (self.location))
        self.read = ReadRulesDisk(self.logging, self.location)

        while self.loop():
            try:
                self.__active_rules = dict(self.read.readDirectory().items() + self.rules.items())
                break
            except Exception as err:
                self.logging.warning("Problem reading rules directory.  Reason: %s" % (err))
                sleep(1)

        while self.loop():
            try:
                self.__active_rules = dict(self.read.get().items() + self.rules.items())
            except Exception as err:
                self.logging.warning("Problem reading rules directory.  Reason: %s" % (err))
                sleep(1)

    def consume(self, event):
        '''Submits matching documents to the defined queue along with
        the defined header.'''

        for rule in self.__active_rules:
            e = deepcopy(event)
            if self.evaluateCondition(self.__active_rules[rule]["condition"], e["data"]):
                # self.logging.debug("Match for rule %s." % (rule))
                e["header"].update({self.name: {"rule": rule}})
                for queue in self.__active_rules[rule]["queue"]:
                    event_copy = deepcopy(e)
                    for name in queue:
                        if queue[name] is not None:
                            event_copy["header"][self.name].update(queue[name])
                        self.submit(event_copy, self.pool.getQueue(name))
            else:
                pass
                #  self.logging.debug("No match for rule %s." % (rule))

    def evaluateCondition(self, conditions, fields):
        for condition in conditions:
            for field in condition:
                if field in fields:
                    if not self.match.do(condition[field], fields[field]):
                        # self.logging.warning("field %s with condition %s DOES NOT MATCH field %s with value %s" % (field, condition[field], field, fields[field]))
                        return False
                    else:
                        pass
                        # self.logging.warning("field %s with condition %s MATCHES field %s with value %s" % (field, condition[field], field, fields[field]))
                else:
                    # self.logging.warning("field %s does not occur in document.")
                    return False

        return True
