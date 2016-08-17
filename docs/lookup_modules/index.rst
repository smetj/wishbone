==============
Lookup modules
==============

    *Lookup modules provide functions which return values used to initialize
    event modules with dynamic values as parameter values. Lookup modules not
    process events.*

Lookup module functionality can be used when writing servers directly in
Python but are especially useful when creating servers using `bootstrap files`_.
Wishbone modules are initialized using the variables defined in the bootstrap
file. Instead of defining static values, you can define a lookup function
which returns a value by executing some predefined function.  See the
`UpLook`_ library for more information. Lookup functions are defined and
initialized in the `lookups section`_ of the bootstrap file.

**Builtin lookup modules**

Wishbone comes with a set of builtin lookup modules:

.. toctree::
    builtin_modules/index


**Importing modules**

Lookup modules are referenced in the boostrap file using a dotted name which
is the entrypoint for a class.

.. code::

    wishbone.lookup.randominteger


**Lookup modules are classes**

.. code-block:: python

    from random import randint

    class RandomInteger(Lookup):

        def __init__(self, minimum=0, maximum=0):

            self.minimum = minimum
            self.maximum = maximum

        def lookup(self):

            return randint(self.minimum, self.maximum)


Writing a custom lookup function is really simple.  You just have to provide a
class with a `lookup` method which can (optionally) be called using the
arguments values provided in the bootstrap file.


.. code-block:: yaml

    ---
    lookups:
      gimme_a_number:
        module: wishbone.lookup.random_integer
        arguments:
            minimum: 0
            maximum: 99

    modules:
      input:
        module: wishbone.input.testevent
        arguments:
          message : ~~gimme_a_number()
          interval: 1

      stdout:
        module: wishbone.output.stdout

    routingtable:
      - input.outbox            -> stdout.inbox
    ...


.. _UpLook: https://github.com/smetj/uplook
.. _bootstrap files: ../bootstrap/bootstrap_files/index.html#bootstrap-files
.. _lookups section:  ../bootstrap/bootstrap_files/index.html#lookups
