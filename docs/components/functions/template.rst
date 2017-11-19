==================
Template Functions
==================

Template functions return data which can be used inside a template.

Wishbone makes use of `Jinja2`_ for all its templates. Template functions are
functions which can be executed inside templates in order to render data.

Characteristics:

* Template functions are functions which are added to the ``Jinja2`` `list of global functions`_.
* Template functions are classes which base :py:class:`wishbone.function.template.TemplateFunction`.
* Template functions **must** have a ``get()`` method which provides the desired data.

Wishbone comes by default with following builtin template functions:

+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| Name                                                                                                            | Description                                                  |
+=================================================================================================================+==============================================================+
| :py:class:`wishbone.function.template.choice <wishbone.function.template.choice.Choice>`                        | Returns a random element from the provided array.            |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.cycle <wishbone.function.template.cycle.Cycle>`                           | Cycles through the provided array returning the next element.|
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.epoch <wishbone.function.template.epoch.Epoch>`                           | Returns epoch with sub second accuracy as a float.           |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.pid <wishbone.function.template.pid.PID>`                                 | Returns the PID of the current process.                      |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.random_bool <wishbone.function.template.random_bool.RandomBool>`          | Randomly returns True or False                               |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.random_integer <wishbone.function.template.random_integer.RandomInteger>` | Returns a random integer.                                    |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.random_uuid <wishbone.function.template.random_uuid.RandomUUID>`          | Returns a uuid value.                                        |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.random_word <wishbone.function.template.random_word.RandomWord>`          | Returns a random word.                                       |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.regex <wishbone.function.template.regex.Regex>`                           | Regex matching on a string.                                  |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+
| :py:class:`wishbone.function.template.strftime <wishbone.function.template.strftime.STRFTime>`                  | Returns a formatted version of an epoch timestamp.           |
+-----------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------+


See following examples:

* :ref:`Using a template function. <using_a_template_function>`
* :ref:`Creating a template function. <creating_a_template_function>`


.. _Jinja2: http://jinja.pocoo.org/docs/2.9/
.. _list of global functions: http://jinja.pocoo.org/docs/2.9/templates/#list-of-global-functions
