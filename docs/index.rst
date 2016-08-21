========
Wishbone
========

**A Python framework to build event stream processing servers**

https://github.com/smetj/wishbone

What?
=====

Wishbone is a Python framework for building servers to read, process and write
infinite event streams by combining and connecting modules into a `processing
pipeline`_ through which `structured data`_ flows, changes, triggers logic and
interacts with external services.

Wishbone can be used to implement solutions for a wide spectrum of tasks from
building `mashup enablers`_ and `ETL servers`_ to `CEP`_ and `stream
processing`_ servers.

Wishbone comes with a set of useful `builtin event`_ and *lookup* modules with
many more `external modules`_ available and ready to be used.

The goal of the project is to provide a simple and pleasant yet solid and
flexible framework which provides the user a toolbox to be creative building
custom solutions with minimal effort and development time.

How?
====

Servers can be created directly in Python or by bootstrapping an instance
using a YAML file directly from CLI.

    *The following "hello world" example creates a server which continuously
    prints "Hello world!" to STDOUT.*

For this we connect `wishbone.input.testevent`_ to `wishbone.output.stdout`_:

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

    installation/index
    event_modules/index
    lookup_modules/index
    events/index
    router/index
    bootstrap/index
    examples/index


.. _builtin event: event_modules/index.html
.. _structured data: events/index.html
.. _processing pipeline: examples/event_pipeline/index.html
.. _bootstrap: bootstrap/index.html

.. _servers: server/index.html
.. _builtin: modules/builtin%20modules.html
.. _external modules: event_modules/external_modules/index.html
.. _Bootstrap files: server/bootstrap%20files.html
.. _wishbone.input.testevent: event_modules/builtin_modules/index.html#wishbone-input-testevent
.. _wishbone.output.stdout: event_modules/builtin_modules/index.html#wishbone-output-stdout
.. _mashup enablers: https://en.wikipedia.org/wiki/Mashup_(web_application_hybrid)#Mashup_enabler
.. _ETL servers: https://en.wikipedia.org/wiki/Extract,_transform,_load
.. _stream processing: https://en.wikipedia.org/wiki/Stream_processing
.. _CEP: https://en.wikipedia.org/wiki/Complex_event_processing
