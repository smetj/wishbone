=======
Modules
=======

*Event modules* are blocks of code which apply 1 clearly defined function to
the events which pass through.  Event modules are functionally isolated so
they do not directly invoke each other's functionality.  Their only means of
interaction is by passing :py:class:`wishbone.event.Event` objects to each
other's :py:class:`wishbone.Queue` queues.

*Event modules* run as spawned `greenlets`_ in the background and are created
by inheriting :py:class:`wishbone.Actor` as a baseclass.

Modules typically have, but are not limited to, an **inbox**, **outbox**,
**success** and **failed** queue.

*Event modules* are typically initialized and held within a
*:py:class:`wishbone.router.Default` instance.

.. autoclass:: wishbone.Actor
    :members:
    :show-inheritance:
    :inherited-members:


.. warning::

    When a queue is not connected any message submitted to it will be dropped.
    This is by design to ensure queues do not fill up without ever being
    consumed.


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
