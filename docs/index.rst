========
Wishbone
========

**A Python framework to build event stream processing servers**

https://github.com/smetj/wishbone

What?
=====

Wishbone is Python framework geared towards building event stream servers by
combining and connecting `event modules`_, into a
processing pipeline.

The Wishbone Python module comes with a set of useful *event* and *lookup
modules* with different functionalities included.  Developing custom modules
is easy using the Actor baseclass which takes care of the boring things so
development effort is focused to the actual problem solving.

Wishbone's aim is to provide a fun and flexible framework to build creative
solutions in an operations context with short development time for custom
functionality.

How?
====

Servers can be created directly in Python or by bootstrapping a server using a
YAML file directly from CLI.

In the following example we create a server which just prints **"Hello
world!"** to stdout.  For this we connect the wishbone.module.testevent to
wishbone.module.stdout and continuously print the message to the screen.

In Python
---------

.. code-block:: python

    from wishbone.module.testevent import TestEvent
    from wishbone.module.stdout import STDOUT
    from wishbone.router import Default
    from wishbone.actor import ActorConfig

    input_config = ActorConfig("input")
    output_config = ActorConfig("output")

    router = Default()
    router.registerModule(TestEvent, input_config, {"message": "Hello world!"})
    router.registerModule(STDOUT, output_config)
    router.connectQueue("input.outbox", "output.inbox")
    router.start()
    try:
        router.block()
    except KeyboardInterrupt:
        router.stop()


Using a bootstrap file
----------------------

.. code-block:: YAML

    modules:
      input:
        module: wishbone.input.testevent
        arguments:
          message : Hello World!

      stdout:
        module: wishbone.output.stdout

    routingtable:
      - input.outbox            -> stdout.inbox


The server can be started and stopped using the wishbone CLI:

.. code-block:: bash

    $ wishbone debug --config hello_world.yaml



.. toctree::
    :hidden:

    event_modules/index


.. _event modules: modules/index.html
.. _servers: server/index.html
.. _builtin: modules/builtin%20modules.html
.. _external: modules/external%20modules.html
.. _Bootstrap files: server/bootstrap%20files.html
