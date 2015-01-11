#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  modulemanager.py
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

import pkg_resources
import re
from prettytable import PrettyTable
from wishbone.error import ModuleInitFailure, NoSuchModule


class ModuleManager():

    def __init__(self,
                 categories=["wishbone", "wishbone.contrib"],
                 groups=["flow", "encode", "decode", "function", "input", "output"]):
        self.categories = categories
        self.groups = groups

    def exists(self, name):

        '''Returns True when module exists otherwise False'''

        if self.getModuleByName(name) == None:
            return True
        else:
            return False

    def getModule(self, category, group, name):

        m = None
        for module in pkg_resources.iter_entry_points("%s.%s" % (category, group)):
            if module.name == name:
                m = module.load()

        if m == None:
            raise NoSuchModule("Module %s.%s.%s is unknown." % (category, group, name))
        else:
            return m

    def getModulesList(self, category=None):

        if category is None:
            for category in self.categories:
                for group in self.groups:
                    group_name = "%s.%s" % (category, group)
                    groups = [m.name for m in pkg_resources.iter_entry_points(group=group_name)]
                    for m in sorted(groups):
                        yield (category, group, m)
        else:
            groups = [m.name for m in pkg_resources.iter_entry_points(group=category)]
            for m in sorted(groups):
                (c, g) = (category.split('.'))
                yield (c, g, m)

    def getModuleByName(self, name):

        (category, group, name) = name.split('.')
        return self.getModule(category, group, name)

    def getModuleDoc(self, category, group, name):

        try:
            doc = self.getModule(category, group, name).__doc__
            doc = re.search('(\*\*.*?\*\*)(.*)', doc, re.DOTALL).group(2)
            return doc
        except Exception as err:
            return "Unknown. Reason: %s" % (err)

    def getModuleTitle(self, category, group, name):

        try:
            doc = self.getModule(category, group, name).__doc__
            title = re.search('\*\*(.*?)\*\*(.*)', doc).group(1)
            return title
        except Exception as err:
            return "Unknown. Reason: %s" % (err)

    def getModuleTable(self, category=None, group=None, include_groups=[]):

        table = self.__getTable()

        category_header = None
        group_header = None
        all_items = list(self.getModulesList())

        for g in include_groups:
            all_items += list(self.getModulesList(g))

        for (category, group, module) in all_items:
            title = self.getModuleTitle(category, group, module)
            version = self.getModuleVersion(category, group, module)
            if category_header == category:
                category = ""
            else:
                category_header = category
            if group_header == group:
                group = ""
            else:
                table.add_row(["", "", "", "", ""])
                group_header = group
            table.add_row([category, group, module, version, title])

        table.add_row(["", "", "", "", ""])
        return table.get_string()

    def getModuleVersion(self, category, group, name):

        try:
            for module in pkg_resources.iter_entry_points("%s.%s" % (category, group)):
                if module.name == name:
                    return module.dist.version
        except:
            return "?"

    def validateModuleName(self, name):

        '''Validates a module reference name.'''

        if len(name.split('.')) != 3:

            raise ModuleInitFailure('%s is not a valid name structure.  Should be x.x.x' % name)

    def __getTable(self):

        t = PrettyTable(["Category", "Group", "Module", "Version", "Description"])
        t.align["Category"] = "l"
        t.align["Group"] = "l"
        t.align["Module"] = "l"
        t.align["Version"] = "r"
        t.align["Description"] = "l"

        return t
