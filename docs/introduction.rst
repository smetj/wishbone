============
Introduction
============

Wishbone is a Python framework to create event processing servers by defining
a pipeline of inputs and outputs with a number of intermediate processing
stages in between through which events travel.

Wishbone comes as an executable including a wide range of `builtin modules`_.


Modules and Queues
------------------

Modules are `greenlets`_ each with their own specific functionality. They are
created by inheriting :py:class:`wishbone.Actor` as a baseclass. Modules
cannot (and are not supposed to) directly invoke each others functionality.
Their only means of interaction is by passing :py:class:`wishbone.Event`
objects to each other's :py:class:`wishbone.Queue` queues.

Modules typically have, but are **not** limited to, an **inbox**, **outbox**,
**success** and **failed** queue.


Router
------

The :py:class:`wishbone.router.Default` object loads and initializes the
modules defined in the bootstrap file.  It is responsible for setting up the
module's queue connections.

Modules are registered using
:py:func:`wishbone.router.Default.registerModule`. The router takes care of
the proper startup :py:func:`wishbone.router.Default.start` and shutdown
:py:func:`wishbone.router.Default.stop` sequence of the registered modules.

By default, the router connects each module's *metrics* and *logs* queue to a
:py:class:`wishbone.module.Funnel` named **wishbone_metrics** and
**wishbone_logs** respecively.  It's up to user to further organize log and
metric processing by connecting other modules to one of these instances.

Queues are connected to each other with
:py:func:`wishbone.router.Default.connect`.  A queue can only be connected to
1 single queue.  If you need to have *"one to many"* or *"many to one"*
constructions then you need to use :py:class:`wishbone.module.Fanout` or
:py:class:`wishbone.module.Fanout`.


Events
------

:py:class:`wishbone.Event` objects are used to transport data between modules.

Typically `input modules`_ initialize the :py:class:`wishbone.Event` objects
to encapsulate the data coming in from the outside.

On the other hand, `output modules`_ extract the data portion of the event to
submit that outside of the framework.

An event has a *header* and a *data* portion.  Each time an event enters a
module, a namespace with the module instance name is automatically
initialized. :py:data:`wishbone.Event.data` always returns the data portion
of the module which has last written data into the event using
:py:func:`wishbone.Event.setData`.

.. autoclass:: wishbone.Event
    :members:


Gevent
------

Wishbone uses Gevent.  The modules run as cooperatively scheduled greenlets
while taking advantage of the cooperative socket support for network IO.  This
makes Wishbone servers cope best with IO bound tasks.


.. _builtin modules: builtin%20modules.html
.. _input modules: builtin%20modules.html#input-modules
.. _output modules: builtin%20modules.html#output-modules
.. _greenlets: https://greenlet.readthedocs.org/en/latest/