================
Lookup functions
================

Wishbone modules are initialized using the variables defined in the `bootstrap
file`_. Instead of defining static values, you can define a lookup function
which returns a value by executing some predefined function.  See the
`UpLook`_ library for more information. Lookup functions are defined and
initialized in the `lookups section`_ of the bootstrap file.

**Builtin lookup modules**

Wishbone comes with a set of builtin lookup modules:


- :py:func:`wishbone.lookup.choice`
- :py:func:`wishbone.lookup.cycle`
- :py:func:`wishbone.lookup.etcd`
- :py:func:`wishbone.lookup.event`
- :py:func:`wishbone.lookup.pid`
- :py:func:`wishbone.lookup.randombool`
- :py:func:`wishbone.lookup.randominteger`
- :py:func:`wishbone.lookup.randomword`
- :py:func:`wishbone.lookup.uuid`


**Importing modules**

Lookup modules are referenced in the boostrap file with a dotted name:

.. code::

    wishbone.lookup.randominteger

The last part of the dotted name is the actual function which must be
imported.  The above lookup module should be possible to import like:

.. code::

    from wishbone.lookup import randominteger


**Lookup modules are closures**

.. code-block:: python

    def randominteger(min=0, max=100):
        from random import randint

        def randomInteger():
            return randint(min, max)

        return randomInteger

Writing a custom lookup function is really simple.  You just have to create an
*importable* function which can be called using the arguments values provided
in the bootstrap file.  This function then returns the function which can be
called by Wishbone to retrieve the value you're after.

.. _UpLook: https://github.com/smetj/uplook
.. _bootstrap file: bootstrap%20files.html#modules
.. _lookups section:  bootstrap%20files.html#lookups
