================
Writing a module
================

Wishbone is all about making the development of your custom modules as simple
as possible by taking care of the things which distract you from writing the
actual code you want to be working on.

**Example Module**

The following example module evaluates whether an integer is between a
*minimum* and a *maximum* value.  Depending whether that's a case the event
will be submitted to the appropriate queue.

.. literalinclude:: ../examples/biggerandsmaller.py
   :language: python
   :linenos:


Module Explained
----------------

**Make the module importable by Wishbone**

Wishbone uses Python's `setuptools`_ `entrypoint`_ definitions to load
modules. These are defined in the module's setup.py file.

Example:

.. code-block:: python

    entry_points={
        'mymodule.flow': [
            'biggersmaller = biggerandsmaller:BiggerAndSmaller'
        ]
    }

This entrypoint definition allows Wishbone to import the module using
*mymodule.flow.biggersmaller* in the boostrap file.


**Document the module**

The docstring (line 8-32) contains the module's description.  It's encouraged
to document your module in a similarly.  The content of the docstring can be
accessed on CLI using the `show`_ command.


**Inherit baseclass**

A Wishbone module is created by making a class which uses
:py:class::`wishbone.Actor` as a base class (line 3, 6).

This baseclass must be initialized (line 35) with the *actor_config* value
provided when initializing (line 34) the module.

The *actor_config* value is a :py:class:`wishbone.actor.ActorConfig` instance
containing the configuration specific to the modules behavior inside the
Wishbone framework.  This instance is automatically created and provided by
the framework so it's not of any concern when developing the module.


**Creating the required queues**

All the module's queues are stored in :py:attr:`wishbone.pool` which is an
instance of :py:class:`wishbone.queue.QueuePool`.

Besides for the default *failed* and *success* queues, it's left up to the
developer to create the required queues.  Creating queues is done by invoking
the :py:class:`wishbone.queue.QueuePool.createQueue` (line 37, 38, 39).


**Registering a function**

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


**Submitting the event to a queue**

After processing the event it must be submitted to the relevant queue so it
can be forwarded to the next module.

Submitting an event to a queue is done with :py:func:`wishbone.Actor.submit`
(line 48, 50).


**Dealing with exceptions while processing events**

If an *exception* occurs within the registered function (we deliberately
invoke one on line 44) then Wishbone will automatically submit the event to
the module's default **failed** queue.



.. _show: server.html
.. _setuptools: https://pythonhosted.org/setuptools/setuptools.html
.. _entrypoint: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
