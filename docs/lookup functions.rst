================
Lookup functions
================

Wishbone modules are initialized using the variables defined in the `bootstrap
file`_. Instead of defining static values, it is possible to provide a lookup
function which provides the said variable value by executing some predefined
function.  See the `UpLook`_ library for more information.
Lookup functions are defined and initialized in the `lookups section`_ of the
bootstrap file.

Builtin lookup modules
----------------------

Wishbone comes with a set of builtin lookup modules:


- :py:func:`wishbone.lookup.randomword`
- :py:func:`wishbone.lookup.randombool`
- :py:func:`wishbone.lookup.randominteger`
- :py:func:`wishbone.lookup.event`


Importing modules
-----------------

Lookup modules are referenced in the boostrap file with a dotted name:

.. code::

    wishbone.lookup.randominteger

The last part of the dotted name is the actual function which must be
imported.  The above lookup module should be possible to import like:

.. code::

    from wishbone.lookup import randominteger


Lookup modules are closures
---------------------------

.. code-block:: python

    def randominteger(min=0, max=100):
        from random import randint

        def randomInteger():
            return randint(min, max)

        return randomInteger


.. _UpLook: https://github.com/smetj/uplook
.. _bootstrap file: bootstrap%20files.html#modules
.. _lookups section:  bootstrap%20files.html#lookups