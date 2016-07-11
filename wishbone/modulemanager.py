#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  modulemanager.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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
from wishbone.error import NoSuchModule, InvalidModule
from wishbone import Actor
from wishbone.lookup import Lookup


class ModuleManager():

    '''
    Manages the Wishbone modules it can find under the defined entrypoints
    prefixes.

    When initiated it indexes all the Wishbone actor modules it can find in
    the <categories>.<groups> combinations.

    Note:

        A module manager expects to find Wishbone actor based modules as
        entrypoints with prefixes like "wishbone.flow", "wishbone.encode" etc,
        ...*

        Wishbone categories are "wishbone" and "wishbone_contrib" where the
        first holds the "official" builtin modules whereas the latter should
        be the namespace to register communitry contributed (external)
        modules.*

        Each category is divided into 7 groups "flow", "encode", "decode",
        "function", "input", "output", "lookup" which define the type of
        module.*

    Args:

        categories (list): The list of categories to search for <groups>
        groups (list): The list of groups to search for Wishbone actor
            modules.

    '''

    def __init__(self,
                 categories=["wishbone", "wishbone_contrib"],
                 groups=["flow", "encode", "decode", "function", "input", "output", "lookup"]):
        self.categories = categories
        self.groups = groups

    def exists(self, name):

        '''
        Validates whether the module with <name> exists.

        Args:
            name (str): The complete name of the module.

        Returns:
            bool: True if module exists. False otherwise.
        '''

        if self.getModuleByName(name) is None:
            return True
        else:
            return False

    def getModule(self, category, group, name):
        '''
        Returns the module with name <category>.<group>.<name>

        Args:
            category (str): The category name.
            group (str): The group name.
            name (str): The module name.

        Returns:
            class: A ``wishbone.Actor``` or ``wishbone.Lookup`` based class

        Raises:
            NoSuchModule: The module does not exist.
            InvalidModule: There was module found but it was not deemed valid.
        '''

        m = None
        for module in pkg_resources.iter_entry_points("%s.%s" % (category, group)):
            if module.name == name:
                m = module.load()

        if m is None:
            raise NoSuchModule("Module %s.%s.%s cannot be found." % (category, group, name))
        else:
            if issubclass(m, Actor) or issubclass(m, Lookup):
                return m
            else:
                raise InvalidModule("'%s.%s.%s' is not a valid wishbone actor or lookup module." % (category, group, name))

    def getModuleByName(self, name):
        '''
        Returns the module with name <name>

        Args:
            name (str): The complete module name.

        Returns:
            class: A `wishbone.Actor` or `wishbone.Lookup` based class

        Raises:
            NoSuchModule: The module does not exist.
            InvalidModule: There was module found but it was not deemed valid.
        '''

        (category, group, name) = name.split('.')
        m = self.getModule(category, group, name)

        if issubclass(m, Actor) or issubclass(m, Lookup):
            return m
        else:
            raise InvalidModule("'%s.%s.%s' is not a valid wishbone actor or lookup module." % (category, group, name))

    def getModuleList(self):
        '''
        Finds and lists all the modules it can find under the defined
        <category>.<groups> combinations.

        Args:
            category (str): The category name.
            group (str): The group name.
            name (str): The module name.

        Yields:
            tuple: A 3 element tuple: (`category`, `group`, `module`)
        '''
        for category in self.categories:
            for group in self.groups:
                group_name = "%s.%s" % (category, group)
                groups = [m.name for m in pkg_resources.iter_entry_points(group=group_name)]
                for m in sorted(groups):
                    yield (category, group, m)

    def getModuleDoc(self, category, group, name):
        '''
        Returns the docstring of module `category`.`group`.`name`

        Args:
            category (str): The category name.
            group (str): The group name.
            name (str): The module name.

        Returns:
            str: The docstring of the module.

        Raises:
            InvalidModule: The docstring does not have the correct format.
        '''

        doc = self.getModule(category, group, name).__doc__
        doc = re.search('(\*\*.*?\*\*)(.*)', doc, re.DOTALL).group(2)
        if doc is None:
            raise InvalidModule("The module does not seem to have the expected docstring format.")
        else:
            return doc

    def getModuleTitle(self, category, group, name):
        '''
        Returns the title of the module `category`.`group`.`name` docstring.

        Args:
            category (str): The category name.
            group (str): The group name.
            name (str): The module name.

        Returns:
            str: The docstring/module title

        Raises:
            InvalidModule: The docstring does not have the correct format.
        '''

        doc = self.getModule(category, group, name).__doc__
        title = re.search('\*\*(.*?)\*\*(.*)', doc).group(1)
        if title is None:
            raise InvalidModule("The module does not seem to have the expected docstring format.")
        else:
            return title

    def getModuleTable(self):
        '''
        Returns an ascii table of all Wishbone modules with valid entry points.

        Returns:
            str: The ascii table containing all modules.
        '''

        table = self.__getModuleTable()

        category_header = None
        group_header = None
        all_items = list(self.getModuleList())

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
        '''
        Returns the version of the module.

        Args:
            category (str): The category name.
            group (str): The group name.
            name (str): The module name.

        Returns:
            str: The version of the module.
        '''

        try:
            for module in pkg_resources.iter_entry_points("%s.%s" % (category, group)):
                if module.name == name:
                    return module.dist.version
        except:
            return "?"

    def validateModuleName(self, name):
        '''
        Validates a module reference name for the proper format.

        Args:
            name (str): The name to validate.

        Returns:
            bool: True when valid.  False when invalid.
        '''

        if len(name.split('.')) != 3:
            return False
        else:
            return True

    def __getModuleTable(self):
        '''
        Returns a skeleton ascii module table object
        '''

        t = PrettyTable(["Category", "Group", "Module", "Version", "Description"])
        t.align["Category"] = "l"
        t.align["Group"] = "l"
        t.align["Module"] = "l"
        t.align["Version"] = "r"
        t.align["Description"] = "l"

        return t
