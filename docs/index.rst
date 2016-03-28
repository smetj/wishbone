========
Wishbone
========

**A Python framework to build composable event pipeline servers with minimal effort.**

https://github.com/smetj/wishbone

Bootstrap a  server
===================

Wishbone `servers`_ are started with bootstrap file:

.. code-block:: sh

    $ wishbone start --config eventprocessor.yaml


`Bootstrap files`_ define the `builtin`_ and `external`_ modules to initialize and how these should be
connected to each other:

.. image:: intro.png
    :align: right

.. literalinclude:: static/test_setup.yaml
   :language: yaml


Running a server:

.. code-block:: sh

    [smetj@dev-container ~]$ wishbone debug --config simple.yaml
    Instance started in foreground with pid 5434
    2016-02-17T20:42:59 wishbone[5434]: debug output2: Connected queue output2.logs to _logs.output2
    2016-02-17T20:42:59 wishbone[5434]: debug output2: Connected queue output2.metrics to _metrics.output2
    2016-02-17T20:42:59 wishbone[5434]: debug output2: preHook() found, executing
    2016-02-17T20:42:59 wishbone[5434]: debug output2: Initialized.
    2016-02-17T20:42:59 wishbone[5434]: debug output2: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2016-02-17T20:42:59 wishbone[5434]: debug output1: Connected queue output1.logs to _logs.output1
    2016-02-17T20:42:59 wishbone[5434]: debug output1: Connected queue output1.metrics to _metrics.output1
    2016-02-17T20:42:59 wishbone[5434]: debug output1: preHook() found, executing
    2016-02-17T20:42:59 wishbone[5434]: debug output1: Initialized.
    2016-02-17T20:42:59 wishbone[5434]: debug output1: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2016-02-17T20:42:59 wishbone[5434]: debug input: Connected queue input.logs to _logs.input
    2016-02-17T20:42:59 wishbone[5434]: debug input: Connected queue input.metrics to _metrics.input
    2016-02-17T20:42:59 wishbone[5434]: debug input: Connected queue input.outbox to mixing.inbox
    2016-02-17T20:42:59 wishbone[5434]: debug input: preHook() found, executing
    2016-02-17T20:42:59 wishbone[5434]: debug input: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2016-02-17T20:42:59 wishbone[5434]: debug mixing: Connected queue mixing.logs to _logs.mixing
    2016-02-17T20:42:59 wishbone[5434]: debug mixing: Connected queue mixing.metrics to _metrics.mixing
    2016-02-17T20:42:59 wishbone[5434]: debug mixing: Connected queue mixing.one to output1.inbox
    2016-02-17T20:42:59 wishbone[5434]: debug mixing: Connected queue mixing.two to output2.inbox
    2016-02-17T20:42:59 wishbone[5434]: debug mixing: preHook() found, executing
    2016-02-17T20:42:59 wishbone[5434]: debug mixing: Started with max queue size of 100 events and metrics interval of 1 seconds.
    I am output #2: seawater's
    I am output #1: hinders
    I am output #2: stigmatism
    I am output #1: damnedest
    I am output #2: ejects
    I am output #1: legates
    I am output #2: lobos
    I am output #1: punctures
    I am output #2: port
    I am output #1: condominium's
    I am output #2: banqueted
    I am output #1: bucker
    I am output #2: efficiencies
    ... snip ...

.. toctree::
    :hidden:

    introduction
    installation/index
    server/index
    modules/index
    miscellaneous


.. _servers: server/index.html
.. _builtin: modules/builtin%20modules.html
.. _external: modules/external%20modules.html
.. _Bootstrap files: server/bootstrap%20files.html
