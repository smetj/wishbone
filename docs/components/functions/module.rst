================
Module Functions
================
.. _module_functions:

Module functions are functions in a module which are automatically applied to
events when they are consumed from a queue.

Multiple module functions can be chained in order to reach the desired effect.
Module function modify events in one way or another.

Characteristics:

* Module functions are applied to events and modify them.
* Module functions are executed when events are consumed from a queue.
* Module functions are only applied to queue which are consumed by a
  registered function by using
  :py:func:`wishbone.actor.Actor.registerConsumer`.
* When a function returns an error it is logged and skipped and the rest of
  the module functions will be applied.


Wishbone comes by default with following builtin module functions:

+-----------------------------------------------------------------------------------------------+--------------------------------------+
| Name                                                                                          | Description                          |
+===============================================================================================+======================================+
| :py:class:`wishbone.function.module.append <wishbone.function.module.append.Append>`          | Adds a value to an existing list.    |
+-----------------------------------------------------------------------------------------------+--------------------------------------+
| :py:class:`wishbone.function.module.lowercase <wishbone.function.module.lowercase.Lowercase>` | Puts the desired field in lowercase. |
+-----------------------------------------------------------------------------------------------+--------------------------------------+
| :py:class:`wishbone.function.module.set <wishbone.function.module.set.Set>`                   | Sets a field to the desired value.   |
+-----------------------------------------------------------------------------------------------+--------------------------------------+
| :py:class:`wishbone.function.module.uppercase <wishbone.function.module.uppercase.Uppercase>` | Puts the desired field in uppercase. |
+-----------------------------------------------------------------------------------------------+--------------------------------------+

See following examples:

* :ref:`Using a module function. <using_a_module_function>`
* :ref:`Creating a module function. <creating_a_module_function>`
