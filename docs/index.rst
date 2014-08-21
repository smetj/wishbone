========
Wishbone
========
https://github.com/smetj/wishbone

.. currentmodule:: wishbone.module

A Python library and CLI tool to build and manage event pipeline servers with
minimal effort.

Creating a server in Python
===========================

.. code-block:: python

    >>> from wishbone.router import Default
    >>> from wishbone.module import TestEvent
    >>> from wishbone.module import RoundRobin
    >>> from wishbone.module import STDOUT

    >>> router = Default()
    >>> router.registerModule(TestEvent, "input", interval=1)
    >>> router.registerModule(RoundRobin, "mixing")
    >>> router.registerModule(STDOUT, "output1", prefix="I am number one: ")
    >>> router.registerModule(STDOUT, "output2", prefix="I am number two: ")

    >>> router.connect("input.outbox", "mixing.inbox")
    >>> router.connect("mixing.one", "output1.inbox")
    >>> router.connect("mixing.two", "output2.inbox")

    >>> router.start()
    >>> router.block()
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test


.. image:: intro.png
    :align: right


In this example we initialize :class:`wishbone.router.Default` to create a
simple setup in which we connect :py:class:`wishbone.module.TestEvent`, which
does nothing more than generating the word "test" every second, to
:class:`wishbone.module.RoundRobin` which on its turn "roundrobins" the
incoming events to two :class:`wishbone.module.STDOUT` instances which print
all incoming events to STDOUT.


Bootstrapping server from CLI
=============================

Wishbone comes with a CLI tool to bootstrap servers using a YAML formatted
config file.  The bootstrap file describes the modules to initialize and how
the modules should be connected to each other.

Following bootstrap file creates exactly the same setup as shown in the above
example:

.. literalinclude:: examples/test_setup.yaml
   :language: yaml

Bootstrapping the environment is just a matter of invoking the **wishbone**
executable using the *--config* parameter pointing to the bootstrap file.

.. code-block:: sh

    [smetj@indigo ~]$ wishbone debug --config simple.yaml --id docker
    2014-08-06T23:17:41 wishbone[6609]: debug metrics_funnel: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug metrics_funnel: preHook() found, executing
    2014-08-06T23:17:41 wishbone[6609]: debug logs_funnel: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug logs_funnel: preHook() found, executing
    2014-08-06T23:17:41 wishbone[6609]: debug mixing: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug mixing: preHook() found, executing
    2014-08-06T23:17:41 wishbone[6609]: debug input: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug input: preHook() found, executing
    2014-08-06T23:17:41 wishbone[6609]: debug output1: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug output2: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug log_stdout: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug log_format: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug syslog: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-08-06T23:17:41 wishbone[6609]: debug syslog: preHook() found, executing
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    ^C2014-08-06T23:18:09 wishbone[6609]: debug syslog: postHook() found, executing
    2014-08-06T23:18:09 wishbone[6609]: debug syslog: postHook() found, executing
    2014-08-06T23:18:09 wishbone[6609]: informational input: Stopped producing events.
    [smetj@indigo ~]$


Contents:

.. toctree::
    :maxdepth: 2

    installation
    introduction
    wishbone module
    router
    builtin modules
    bootstrap
    patterns
    components

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`