=======
Modules
=======

Modules are `greenlets`_ each with their own specific functionality. They are
created by inheriting :py:class:`wishbone.Actor` as a baseclass. Modules
cannot and are not supposed to directly invoke each others functionality.
Their only means of interaction is by passing :py:class:`wishbone.event.Event`
objects to each other's :py:class:`wishbone.Queue` queues.

Modules typically have, but are **not** limited to, an **inbox**, **outbox**,
**success** and **failed** queue.

.. warning::

    When a queue is not connected to another queue then submitting a message
    into it will result into the message being dropped.  This is by design to
    ensure queues do not fill up without ever being consumed.


.. toctree::
    :hidden:

    module types
    events
    bulk events
    logs and metrics
    writing a module
    builtin modules
    external modules


.. _greenlets: https://greenlet.readthedocs.org/en/latest/
