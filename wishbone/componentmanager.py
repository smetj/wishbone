#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  componentmanager.py
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

import pkg_resources
from prettytable import PrettyTable
from wishbone.error import InvalidComponent, NoSuchComponent
from wishbone.actor import Actor
from wishbone.function.template import TemplateFunction
from wishbone.function.module import ModuleFunction
from wishbone.protocol import Encode
from wishbone.protocol import Decode


class ComponentManager():

    '''
    Loads Wishbone components and information.

    When initiated it indexes all the Wishbone components found in the
    available ``<namespace>.<component_type>.<category>`` combinations.

    A complete component reference would then be something like:
    ``wishbone.module.process.modify``

    - ``wishbone`` is the namespace
    - ``module`` is the component type
    - ``process`` is the component category
    - ``modify`` is the name of the component

    Note:

        The default Wishbone namespaces are ``wishbone``, for the builtin
        modules and ``wishbone_contrib`` or ``wishbone_external`` for
        externally developed components.

        There exist 3 component types:
            - module
            - function
            - protocol

    Args:

        namespace (list): The list of namespaces to search for <categories>
        module_categories (list): The list of module categories to search
        function_categories (list): The list of function categories to search
    '''

    COMPONENT_TYPES = [
        "protocol",
        "module",
        "function",
    ]

    def __init__(self,
                 namespace=["wishbone", "wishbone_contrib", "wishbone_external"],
                 protocol_categories=["encode", "decode"],
                 module_categories=["flow", "input", "output", "process"],
                 function_categories=["template", "module"],
                 ):
        self.namespace = namespace
        self.component_types = ["protocol", "module", "function"]
        self.protocol_categories = protocol_categories
        self.module_categories = module_categories
        self.function_categories = function_categories

    def exists(self, name):

        '''
        Validates whether the component with <name> exists.

        Args:
            name (str): The complete name of the component.

        Returns:
            bool: True if component exists. False otherwise.
        '''

        if self.getComponentByName(name) is None:
            return False
        else:
            return True

    def getComponent(self, namespace, component_type, category, name):
        '''
        Returns the module with name <namespace>.<component_type>.<category>.<name>

        <namespace>.<component_type>.<category>.<name> must be an entrypoint.

        Args:
            namespace (str): The component namespace
            component_type (str): The component type.
            category (str): The component category.
            name (str): The component name.

        Returns:
            class: A ``wishbone.Actor``, ``wishbone.Function`` based class

        Raises:
            NoSuchComponent: The module does not exist.
            InvalidComponent: There was module found but it was not deemed valid.
        '''

        m = None
        for module in pkg_resources.iter_entry_points("%s.%s.%s" % (namespace, component_type, category)):
            if module.name == name:
                m = module.load()
                break

        if m is None:
            raise NoSuchComponent("Component %s.%s.%s.%s cannot be found." % (namespace, component_type, category, name))
        else:
            if issubclass(m, Actor) or issubclass(m, TemplateFunction) or issubclass(m, ModuleFunction) or issubclass(m, Decode) or issubclass(m, Encode):
                return m
            else:
                raise InvalidComponent("'%s.%s.%s.%s' is not a valid wishbone component." % (namespace, component_type, category, name))

    def getComponentByName(self, name):
        '''
        Returns the module with name ``name``.
        ``name`` should be a valid entrypoint.

        Args:
            name (str): The complete module name.

        Returns:
            class: A `wishbone.Actor` or `wishbone.Function` based class

        Raises:
            NoSuchComponent: The module does not exist.
            InvalidComponent: There was module found but it was not deemed valid.
        '''
        self.validateComponentName(name)
        (namespace, component_type, category, name) = name.split('.')
        return self.getComponent(namespace, component_type, category, name)

    def getComponentList(self):
        '''
        Finds and lists all the components found at the defined
        <namespace>.<module_categories>. combinations.

        Yields:
            tuple: A 4 element tuple: (`namespace`, `component_type`, `category`, `name`)
        '''

        for namespace in self.namespace:
            for category in sorted(self.protocol_categories):
                prefix = "%s.protocol.%s" % (namespace, category)
                for item in [m.name for m in pkg_resources.iter_entry_points(group=prefix)]:
                    yield (namespace, "protocol", category, item)
            for category in sorted(self.function_categories):
                prefix = "%s.function.%s" % (namespace, category)
                for item in [m.name for m in pkg_resources.iter_entry_points(group=prefix)]:
                    yield (namespace, "function", category, item)
            for category in sorted(self.module_categories):
                prefix = "%s.module.%s" % (namespace, category)
                for item in [m.name for m in pkg_resources.iter_entry_points(group=prefix)]:
                    yield (namespace, "module", category, item)

    def getComponentDoc(self, namespace, component_type, category, name):
        '''
        Returns the docstring of module `namespace`.`category`.`group`.`name`

        Args:
            namespace (str): The namespace value.
            component_type (str): The component type.
            category (str): The component type category.
            name (str): The component name name.

        Returns:
            str: The docstring of the module.

        Raises:
            InvalidModule: The docstring does not have the correct format.
        '''

        doc = self.getComponent(namespace, component_type, category, name).__doc__

        if doc is None:
            raise InvalidComponent("Component '%s' does not seem to have the expected docstring format." % ())
        else:
            return doc

    def getComponentTitle(self, namespace, component_type, category, name):
        '''
        Returns the title of the module `category`.`group`.`name` docstring.

        Args:
            namespace (str): The namespace value.
            component_type (str): The component type.
            category (str): The component type category.
            name (str): The component name name.

        Returns:
            str: The docstring/module title

        Raises:
            InvalidModule: The docstring does not have the correct format.
        '''

        doc = self.getComponent(namespace, component_type, category, name).__doc__
        if doc is None:
            return "The component doesn't have a docstring."

        title = doc.strip().split('\n')[0].strip('*')
        if title is None:
            raise InvalidComponent("Component '%s' does not seem to have the expected docstring format." % (name))
        else:
            return title

    def getComponentTable(self):
        '''
        Returns an ascii table of all found Wishbone components.

        Returns:
            str: The ascii table containing all modules.
        '''

        table = self.__getComponentTable()
        namespace_header = None
        component_type_header = None
        category_header = None

        for (namespace, component_type, category, name) in self.getComponentList():

            title = self.getComponentTitle(namespace, component_type, category, name)
            version = self.getComponentVersion(namespace, component_type, category, name)

            if namespace_header == namespace:
                namespace = ""
            else:
                namespace_header = namespace
                component_type_header = None
                category_header = None

            if component_type_header == component_type:
                component_type = ""
            else:
                component_type_header = component_type

            if category_header == category:
                category = ""
            else:
                category_header = category
                table.add_row(["", "", "", "", "", ""])

            table.add_row([namespace, component_type, category, name, version, title])

        table.add_row(["", "", "", "", "", ""])
        return table.get_string()

    def getComponentVersion(self, namespace, component_type, category, name):
        '''
        Returns the version of the module.

        Args:
            namespace (str): The namespace value.
            component_type (str): The component type.
            category (str): The component type category.
            name (str): The component name name.

        Returns:
            str: The version of the module.
        '''

        try:
            for module in pkg_resources.iter_entry_points("%s.%s.%s" % (namespace, component_type, category)):
                if module.name == name:
                    return module.dist.version
        except:
            return "?"

    def validateComponentName(self, name):
        '''
        Validates a component reference name for the proper format.

        Args:
            name (str): The name to validate.

        Returns:
            bool: True when valid.  False when invalid.
        '''

        if len(name.split('.')) != 4:
            raise InvalidComponent("Component name '%s' should consist out of 4 parts." % (name))
        if name.split('.')[1] not in self.COMPONENT_TYPES:
            raise InvalidComponent("Component name '%s' has an invalid component type name." % (name))

        return True

    def __getComponentTable(self):
        '''
        Returns a skeleton ascii module table object
        '''

        t = PrettyTable(["Namespace", "Component type", "Category", "Name", "Version", "Description"])
        t.align["Namespace"] = "l"
        t.align["Component type"] = "l"
        t.align["Category"] = "l"
        t.align["Name"] = "l"
        t.align["Version"] = "r"
        t.align["Description"] = "l"
        return t
