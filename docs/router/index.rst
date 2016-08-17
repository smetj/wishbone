======
Router
======

    *A router is responsible for initializing and holding all event modules,
    connecting their queues and organize the event flow between them.*

The router object plays a central role in the Wishbone setup.  When
bootstrapping an instances using the CLI tooling you are not really exposed to
it (though the routing table might give a hint), however if you create a
server directly in Python you will always first have to initialize a
``Router`` instance:

.. code-block:: python

    input_config = ActorConfig("input")
    output_config = ActorConfig("output")

    router = Default()
    router.registerModule(TestEvent, input_config, {"message": "Hello world!"})
    router.registerModule(STDOUT, output_config)
    router.connectQueue("input.outbox", "output.inbox")
    router.start()
    router.block()



Multiple routers can be initialized which run inside the same ``process``.

.. code-block:: python

    from wishbone.actor import ActorConfig
    from wishbone.router import Default
    from wishbone.module.testevent import TestEvent
    from wishbone.module.stdout import STDOUT

    input_config = ActorConfig("input")
    output_config = ActorConfig("output")

    router_1 = Default()
    router_1.registerModule(TestEvent, input_config, {"message": "Hello world from router instance 1!"})
    router_1.registerModule(STDOUT, output_config)
    router_1.connectQueue("input.outbox", "output.inbox")
    router_1.start()

    router_2 = Default()
    router_2.registerModule(TestEvent, input_config, {"message": "Hello world from router instance 2!"})
    router_2.registerModule(STDOUT, output_config)
    router_2.connectQueue("input.outbox", "output.inbox")
    router_2.start()

    router_1.block()
    router_2.block()


.. code-block:: bash

    $ python 2_routers.py
    Hello world from router instance 1!
    Hello world from router instance 2!
    Hello world from router instance 1!
    Hello world from router instance 2!
    Hello world from router instance 1!
    Hello world from router instance 2!


.. note::

    If desired, multiple ``Router`` instances can each run into their own
    ``Process`` using `gipc`_.  This is what
    :py:class:`wishbone.bootstrap.Dispatch` does.




Wishbone comes with the default :py:class:`wishbone.router.Default` router implementation.

.. autoclass:: wishbone.router.Default
    :members:

.. _gipc:
