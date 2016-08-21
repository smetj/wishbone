==============
Event pipeline
==============

The following bootstrap file uses the
:py:class:`wishbone.module.testevent.TestEvent` module to generate a message
every second.  To provide the content of the message is uses the `lookup
module`_ :py:class:`wishbone.lookup.random_word.RandomWord` to generate the
content of the message.

The generated event is then passed onto the `flow module`_
:py:class:`wishbone.module.roundrobin.RoundRobin` which *"roundrobins"* the
event over 2 :py:class:`wishbone.module.stdout.STDOUT` `output modules`_ which
print the incoming event to STDOUT.


.. image:: /intro.png
    :align: right

.. code-block:: yaml

    lookups:
      randomword:
        module: wishbone.lookup.randomword
        arguments:
          interval: 1

    modules:
      input:
        module: wishbone.input.testevent
        description: I generate a random word.
        arguments:
          message: ~~randomword()

      mixing:
        module: wishbone.flow.roundrobin
        description: I roundrobin incoming messages

      output1:
        module: wishbone.output.stdout
        description: I write incoming messages to stdout.
        arguments:
          prefix: "I am output #1: "

      output2:
        module: wishbone.output.stdout
        description: I write incoming messages to stdout.
        arguments:
          prefix: "I am output #2: "

    routingtable:
      - input.outbox  -> mixing.inbox
      - mixing.one    -> output1.inbox
      - mixing.two    -> output2.inbox



The server can be bootstrapped on CLI by issuing following command:

.. code-block:: bash

  $ wishbone debug --config bootstrap.yaml


.. _lookup module: ../../lookup_modules/index.html
.. _flow module: ../../event_modules/module_types/index.html#flow-modules
.. _output modules: ../../event_modules/module_types/index.html#output-modules
