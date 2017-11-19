.. _modules:
=======
Modules
=======

Modules are isolated pieces of code which do not directly invoke each others
functionality.  They merely act upon the messages coming in to its queues and
submit messages into another queue for the next module to process.
Modules run as greenthreads.

Wishbone comes with a set of builtin modules.  Besides these, there's a
collection of :ref:`external modules <external modules>` available which are
developed and released seperately from Wishbone itself.

Wishbone has following module types:

.. toctree::
    input
    output
    flow
    process


**Characteristics**


* If a queue is not connected to another queue then the messages submitted to
  it are dropped.  This is by design to prevent queues from filling up.

* Each module has by default a ``_success`` and ``_failed`` queue to which a
  copy of passing events is submitted if it has been processed successfully or
  not.

* Each module has by default a ``_logs`` and ``_metrics`` queue to which logs
  and metrics are submitted respectively.

**Module configuration**


A module has an arbirary number of parameters but always needs to accept
:py:class:`wishbone.actorconfig.ActorConfig` which passes Wishbone specific
the characteristics to it:


.. code-block:: python

    from wishbone.module.generator import Generator
    from wishbone.actor import ActorConfig

    actor_config = ActorConfig(
        name='generator'
        size=100
        frequency=1,
        template_functions={},
        description="This is a fizzbuzz exaple"
    )
    test_event = Generator(actor_config, payload="test")

    test_event.pool.queue.outbox.disableFallThrough()
    test_event.start()

    event = getter(test_event.pool.queue.outbox)
    assert event.get() == "test"


.. autoclass:: wishbone.actorconfig.ActorConfig
    :members:

