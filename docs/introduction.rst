============
Introduction
============

.. note::

    Wishbone currently uses Gevent.  The modules run as cooperatively
    scheduled greenlets while taking advantage of the cooperative socket
    support for network IO.  This makes Wishbone servers cope best with IO
    bound tasks.

Modules and Queues
------------------

Modules are `greenlets`_ each with their own specific functionality. They are
created by inheriting :py:class:`wishbone.Actor` as a baseclass. Modules
cannot and are not supposed to directly invoke each others functionality.
Their only means of interaction is by passing :py:class:`wishbone.Event`
objects to each other's :py:class:`wishbone.Queue` queues.

Modules typically have, but are **not** limited to, an **inbox**, **outbox**,
**success** and **failed** queue.

.. warning::

    When a queue is not connected to another queue then submitting a message
    into it will result into the message being dropped.  This is by design.


Router
------

The :py:class:`wishbone.router.Default` object loads and initializes the
modules defined in the bootstrap file.  It is responsible for setting up the
module queue connections.

By default, the router connects each module's *metrics* and *logs* queue to a
:py:class:`wishbone.module.Funnel` named **wishbone_metrics** and
**wishbone_logs** respecively.  It's up to user to further organize log and
metric processing by connecting other modules to one of these instances.

If wishbone is started in debug mode and queue **wishbone_logs** isn't
connected to another queue then the router will connect the **wishbone_logs**
module instance to a :py:class:`wishbone.module.HumanLogFormat` module
instance which on its turn is connected to a
:py:class:`wishbone.module.STDOUT` module instance.


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



.. _executable: cli%20options.html
.. _builtin modules: builtin%20modules.html
.. _input modules: builtin%20modules.html#input-modules
.. _output modules: builtin%20modules.html#output-modules
.. _greenlets: https://greenlet.readthedocs.org/en/latest/