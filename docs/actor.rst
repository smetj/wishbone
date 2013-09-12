=====
Actor
=====

Introduction
------------

Modules are isolated blocks of code (greenlets) each with their own specific
functionality. They are created by simply inheriting
:py:class:`wishbone.Actor` as a baseclass. Modules cannot directly invoke each
others functionality. Their only means of interaction is by passing messages
or events to each other's :py:class:`wishbone.tools.WishboneQueue` queues.
Modules typically have, but are not limited to, an inbox and outbox queue.

Queues always live inside a :py:class:`wishbone.tools.QueuePool` which,
besides offering some convenience functions, is nothing more than a container
to centralize all the queues of the module. Typically, modules consume each
event entering the inbox queue using the :py:func:`wishbone.Actor.consume`
function where the event can be processed and after which it is submitted to
the module's outbox queue from where it can be forwarded again to another
module's queue.

Example
-------

As an example, let's make a module which reverses the content of incoming
events and optionally converts the first letter into a capital.

.. literalinclude:: examples/reversedata.py
   :language: python
   :linenos:

--------

So let's break down what we are seeing here:

We inherit the Actor base class [4] and initialize it [21].  We pass it the a
name and the :py:data:`setupbasic` parameter [21].  The setupbasic parameter
does nothing than creating an inbox and outbox queue and registring the
consume() function as the function which is going to process the events
arriving to inbox by calling the :py:func:`wishbone.Actor.createQueue` and
:py:func:`wishbone.Actor.registerConsumer` in the background.

When :py:data:`setupbasic` is False you will have to create the required
queues and register the required consume yourself.


Wishbone modules can produce log messages [24] using the functions from
:py:class:`wishbone.tools.QLogging`.  Logs are collected by the router and can
be forwarded to other modules for further processing, so we don't need to
worry any further about that.

Our module itself accepts 1 parameter [21] which we can use to modify its
behaviour and which we can use when registering the module in the router using
:py:func:`wishbone.router.Default.register`.

In the background, the Actor module takes care of consuming the events
arriving to the inbox and invoking the :py:func:`wishbone.Actor.consume` [26]
on each one of them.  Events always have following format:

.. code-block:: python

    { "header":{}, "data": object }

So we change the content of data [28-34] according to the modules behaviour.

Last but not least, our modified event needs to go to another module.
Remember modules don't communicate directly to each other? That's why we put
them into the outbox queue [36] for another module to consume.

And that's it.  Save your module and make sure you can import it as a regular
Python module and that you can import it an entrypoint.


--------

.. autoclass:: wishbone.Actor
    :members:
    :show-inheritance:
    :inherited-members:

--------

.. autoclass:: wishbone.tools.QueuePool
    :members:

--------

.. autoclass:: wishbone.tools.WishboneQueue
    :members:

--------

.. autoclass:: wishbone.tools.QLogging
    :members:
