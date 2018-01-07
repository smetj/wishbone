Creating a module
=================

.. _creating_a_module:

.. contents::

The following example module evaluates whether an event containing an integer
value is between a *minimum* and a *maximum*.  Depending on whether the value
is higher or lower the event will be routed to the appropriate queue.

.. literalinclude:: ../static/examples/higherlower.py
   :language: python

Document the module
-------------------

The docstring (line 6-29) contains the module's description.  It's encouraged
to document your module in a similar fashion.  The content of the docstring
can be accessed on CLI using the
:ref:`wishbone show <wishbone_executable_show>` command.

.. code-block:: sh

    $ wishbone show --docs wishbone_contrib.module.flow.higherlower


Base the correct class
----------------------

A module should base (line 5) one of the four :ref:`four modules types. <module_types>`

Since this example module is applying logic of some sort to its incoming
events to decide which queue to submit the event to without actually modifying
its payload we choose type :ref:`flow module <flow>`.

The first parameter of a Wishbone module must **always** be ``actor_config``
which on its turn is used to initialize the base class (line 32).

The ``actor_config`` parameter is a :py:class:`wishbone.actorconfig.ActorConfig`
instance which configures the module's behavior within the Wishbone framework.


Creating queues
---------------

All the module's queues are stored in :py:attr:`wishbone.pool` which is an
instance of :py:class:`wishbone.queue.QueuePool`.
:py:attr:`wishbone.pool` is created by basing the module base class.

Besides for the default ``_failed`` and ``_success`` queues, it's left up to the
developer to make sure the necessary queues are created.

Creating queues is done by invoking the
:py:class:`wishbone.queue.QueuePool.createQueue` (line 43-46). In the case of
this specific :ref:`flow module <flow>` we will create ``inbox``, ``higher``,
``lower``, ``equal``.

Registering a function
----------------------

The modules incoming events are to its ``inbox`` queue. We need to register a
function which takes care of processing the events in the ``inbox`` queue.
Once we have registered such a function, Wishbone will take care of draining
the queue and applying the registered ``function`` to all its events.

Registering such a function is done by applying
:py:func:`wishbone.actor.Actor.registerConsumer` (line 47). The function should have
1 parameter accepting the :py:class:`wishbone.event.Event` instances.


Handling dynamic parameter values
---------------------------------

This is an important topic. Somehow the module needs to know where in the
event it can find the integer value to work with.

There are 2 different approaches to this:

Define the field as a parameter
+++++++++++++++++++++++++++++++

In this case we make the field where to find the integer configurable.
The module's parameters could look like this:

.. code-block:: python

        def __init__(self, actor_config, base=100, field="data"):

The ``consume`` function then could look something like this:

.. code-block:: python

        if event.get(self.kwargs.field) > event.kwargs.base:
            self.submit(event, self.pool.queue.higher)
        elif event.get(self.kwargs.field) < event.kwargs.base:
            self.submit(event, self.pool.queue.lower)
        else:
            self.submit(event, self.pool.queue.equal)

Define the value as a template value
++++++++++++++++++++++++++++++++++++

*This is the technique we use in this example*

We can also pass a template as a parameter which fetches the desired value
from the event. Each time an event enters a registered version, then Wishbone
stores a rendered version of ``self.kwargs`` (the modules parameters) under
``event.kwargs`` using the content of the event itself.

So let's say that incoming events have following :py:class:`wishbone.event.Event` format:

.. code-block:: json

    {
    "bulk": false,
    "cloned": false,
    "data": 99,
    "errors": {},
    "tags": [],
    "timestamp": 1515239271.0001013,
    "tmp": {},
    "ttl": 254,
    "uuid": "1bb5301c-36d6-4a6e-b039-c310eb9a4d85",
    "uuid_previous": []
    }

We can have the bootstrap file initialize the module as such:

.. code-block:: yaml

    evaluate:
        module: wishbone_contrib.module.flow.higherlower
        arguments:
            base: 50
            value: '{{data}}'

Wishbone resolves the (Jinja2) template ``{{data}}`` then into the desired value and store it under ``event.kwargs.value``.
Hence we can do:

.. code-block:: python

        if event.kwargs.value > event.kwargs.base:


Submitting an event to a queue
------------------------------

After processing the event it must be submitted to the relevant queue so it
can be forwarded to the next module.

Submitting an event to a queue should be done by using :py:func:`wishbone.actor.Actor.submit`
(line 55, 57, 59).


Dealing with errors
-------------------

If an ``exception`` occurs inside the registered function then Wishbone will
automatically submit the event to the module's default ``_failed`` queue.
Therefor it is important to allow errors to raise. On the contrary, when the
event has been handled without exceptions then it is also submitted to the
modules ``_success`` queue.

Taking advantage of this behavior is useful to setup error handling
constructions.

Provide an entrypoint
---------------------

Wishbone uses Python's `setuptools`_ `entrypoint`_ definitions to load
modules. These are defined in the module's setup.py file.

Example:

.. code-block:: python

    entry_points={
        'wishbone_contrib.module.flow': [
            'higherlower = higherlower:HigherLower'
        ]
    }

This entrypoint definition allows Wishbone to import the module using
``wishbone_contrib.module.flow.higherlower`` in the boostrap file.

.. _show: /bootstrap/commands/index.html#show
.. _setuptools: https://pythonhosted.org/setuptools/setuptools.html
.. _entrypoint: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
