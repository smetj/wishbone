========
Wishbone
========

**A Python framework to build composable event pipeline middleware with minimal effort.**

https://github.com/smetj/wishbone

.. image:: intro.png
    :align: right


Why should I use it?
====================

You need a server to accept data from A, process it and submit it to B.

Off the shelve you can:

- Make use of the many `builtin modules`_
- Manage and run servers on `command line`_
- Bootstrap servers using `config files`_
- Shape powerful event processing functionality `without programming`_
- Convert and ship Wishbone server `logs and metrics`_ to your liking
- Flexibly deal with errors
- Construct versatile infra related patterns
- Easily adapt and extend functionality to respond to ever changing infra environments
- Make the processed events "tangible"

And when you really need custom functionality:

Focus on creating the actual solution in Python whilst benefiting from all of the above...


Bootstrap a  server
===================

Wishbone `servers`_ are started with bootstrap file:

.. code-block:: sh

    $ wishbone start --config eventprocessor.yaml


`Bootstrap files`_ define the modules_ to initialize and how these should be
connected to each other:

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
.. _modules: modules/builtin%20modules.html
.. _Bootstrap files: server/bootstrap%20files.html
.. _builtin modules: modules/builtin%20modules.html
.. _command line: server/index.html
..  server/bootstrap%20files.html
.. _logs and metrics: modules/logs%20and%20metrics.html
.. _focus on the fun stuff, programming the solution in Python.: modules/writing%20a%20module.html
.. _config files: server/bootstrap%20files.html
