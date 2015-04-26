================
Writing a module
================

Wishbone is all about making the development of your custom modules as simple
as possible by taking care of the things which distract you from writing the
actual code you want to be working on.

Example Module
--------------

The following example module evaluates whether an integer is between a
*minimum* and a *maximum* value.  Depending whether that's a case the event
will be submitted to the appropriate queue.

.. literalinclude:: examples/biggerandsmaller.py
   :language: python
   :linenos:


Module Explained
----------------

Make the module importable by Wishbone
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wishbone uses Python's `setuptools`_ `entrypoint`_ definitions to load
modules. These are defined in the module's setup.py file.

Example:

.. code-block:: python

    entry_points={
        'wishbone.contrib.flow': [
            'biggersmaller = biggerandsmaller:BiggerAndSmaller'
        ]
    }

The entrypoint definition would allow Wishbone to import the module by
referring to *wishbone.contrib.flow.biggersmaller* int he boostrap file.


Document the module
~~~~~~~~~~~~~~~~~~~

The docstring (line 5-20) contains the module's description.  It's encouraged
to document your module in a similar way.  The contenet of the docstring can
be accessed on CLI using the `show`_ command.


Inherit baseclass
~~~~~~~~~~~~~~~~~

A Wishbone module is created by making a class which uses
:py:class::`wishbone.Actor` as a base class (line 3, 6).

This baseclass must be initialized (line 35) with the *actor_config* value
provided when initializing (line 34) the module.

The *actor_config* value is a :py:class:`wishbone.actor.ActorConfig` instance
containing the configuration specific to the modules behaviour inside the
Wishbone framework.  This instance is automatically created and provided by
the framework so it's not of any concern when developing the module.

Creating the required queues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Al the module's queues are available under :py:attr:`wishbone.pool` which is
an instance of :py:class:`wishbone.queue.QueuePool`.

Besides for the default *failed* and *success* queues, it's left up to the
developer to create the required queues.  Creating queues is done by invoking
the :py:class:`wishbone.queue.QueuePool.createQueue` (line 37, 38, 39).

Registering a function
~~~~~~~~~~~~~~~~~~~~~~

For this specific module, we're expecting that data events arrive to the
**inbox** queue.  Wishbone takes care of draining that queue and applying the
events to the function responsible for processing the event.

You need to have such a function, otherwise events will not get consumed for
the queue and the therefor the queue will just fill up without anything
happening.

Registering such a function is done with
:py:func:`wishbone.Actor.registerConsumer` (line 40).  The function consuming
the events (line 42) must have 1 parameter to receive the
events(:py:class:`wishbone.Event`).

Submitting the event to a queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After processing the event it must be submitted to the relevant queue so it
can be further processed by the next module.

Submitting an event to a queue is done with :py:func:`wishbone.Actor.submit`
(line 48, 50).

Dealing with whilst processing events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an *exception* happens within the registered function (we deliberately
invoke one on line 44) then Wishbone will automatically submit the event to
the module's default **failed** queue.

Example bootstrap file
----------------------

The following bootstrap file would produce an integer between 1 and 100
(see :py:func:`wishbone.lookup.randominteger`).

.. literalinclude:: examples/biggerandsmaller.yaml
   :language: yaml
   :linenos:

That would produce following output:


.. code-block:: sh

    $ wishbone debug --config biggerandsmaller.yaml
    Instance started in foreground with pid 12340
    ... snip ...
    The value is outside the defined scope: 33
    The value is outside the defined scope: 44
    The value is outside the defined scope: 36
    The value is outside the defined scope: 20
    The value is outside the defined scope: 8
    The value is inside the defined scope: 62
    The value is inside the defined scope: 91
    The value is outside the defined scope: 43
    The value is outside the defined scope: 49
    The value is inside the defined scope: 89
    The value is inside the defined scope: 75
    The value is outside the defined scope: 38
    The value is outside the defined scope: 26
    The value is outside the defined scope: 5
    ... snip ...



.. _show: server.html
.. _setuptools: https://pythonhosted.org/setuptools/setuptools.html
.. _entrypoint: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
