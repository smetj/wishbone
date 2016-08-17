=============
Event Modules
=============

    *Event modules are building blocks which perform 1 clearly defined action
    to the events passing through them.*


Event modules are functionally isolated blocks of code which do not directly
invoke each other's functionality.  They only interact by passing
:py:class:`wishbone.event.Event` instances to each other's
:py:class:`wishbone.Queue` queues from where the incoming events are consumed
and processed by a function registered by
:py:func:`wishbone.Actor.registerConsumer`.

*Event modules* run as `Gevent greenlets`_ in the background and are created
by inheriting :py:class:`wishbone.Actor` as a baseclass and live inside a
:py:class:`wishbone.router.Default` instance.

Modules typically have, but are not limited to an **inbox**, **outbox**,
**success** and **failed** queue.

A queue can only be connected to 1 single queue.

.. note::

  If you need to have *"one to many"* or *"many to one"* connections then you
  can use the  :py:class:`wishbone.module.Fanout` and
  :py:class:`wishbone.module.Fanout` modules.

The :py:class:`wishbone.Actor` baseclass must be initialized by passing a
:py:class:`wishbone.actor.ActorConfig` instance which controls the behavior of
the module instance.

.. autoclass:: wishbone.Actor
    :members:
    :show-inheritance:
    :inherited-members:


.. warning::

    When a queue is not connected any message submitted to it will be dropped.
    This is by design to ensure queues do not fill up without ever being
    consumed.


.. toctree::
    module_types/index
    builtin_modules/index
    external_modules/index

.. _greenlets: https://greenlet.readthedocs.org/en/latest/
.. _Gevent greenlets: http://www.gevent.org/gevent.html#greenlet-objects
