.. Wishbone documentation master file, created by
   sphinx-quickstart on Wed Aug  7 21:08:21 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
Wishbone
========
https://github.com/smetj/wishbone

.. currentmodule:: wishbone.module

A Python library to build and CLI tool to manage asynchronous coroutine based
event pipeline servers with minimal effort.

Works on python 2.7+ and PyPy 2.3.1+

.. image:: intro.png
    :align: right

.. code-block:: python

    >>> from wishbone.router import Default
    >>> from wishbone.module import TestEvent
    >>> from wishbone.module import RoundRobin
    >>> from wishbone.module import STDOUT

    >>> router = Default()
    >>> router.initializeModule(TestEvent, "input", interval=1)
    >>> router.initializeModule(RoundRobin, "mixing")
    >>> router.initializeModule(STDOUT, "output1", prefix="I am number one: ")
    >>> router.initializeModule(STDOUT, "output2", prefix="I am number two: ")

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


This example we initialize the :class:`wishbone.router.Default` router to
create a simple setup in which we connect the :py:class:`TestEvent` input
module, which does nothing more than generating the word "test" every second,
to the :class:`wishbone.module.RoundRobin` module which on its turn
"roundrobins" the incoming events to 2 :class:`wishbone.module.STDOUT` module
instances which print all incoming events to STDOUT.


Bootstrapping
=============

Wishbone comes with a CLI tool to easily bootstrap a server using a YAML
formatted config file.  Following file creates exactly the same environment as
the above example:

.. literalinclude:: examples/test_setup.yaml
   :language: yaml

Bootstrapping the environment is just a matter of invoking the **wishbone**
executable using the --config parameter pointing to the bootstrap file.

.. code-block:: sh

    [smetj@indigo ~]$ wishbone debug --config test.yaml
    2014-07-19T23:56:53 pid-8154 debug metrics_funnel: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug metrics_funnel: preHook() found, executing
    2014-07-19T23:56:53 pid-8154 debug logs_funnel: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug logs_funnel: preHook() found, executing
    2014-07-19T23:56:53 pid-8154 debug mixing: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug mixing: preHook() found, executing
    2014-07-19T23:56:53 pid-8154 debug input: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug input: preHook() found, executing
    2014-07-19T23:56:53 pid-8154 debug output1: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug output2: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug log_stdout: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug log_format: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug syslog: Started with max queue size of 100 events and metrics interval of 1 seconds.
    2014-07-19T23:56:53 pid-8154 debug syslog: preHook() found, executing
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    ^C2014-07-19T23:56:56 pid-8154 debug syslog: postHook() found, executing
    2014-07-19T23:56:56 pid-8154 debug syslog: postHook() found, executing
    2014-07-19T23:56:57 pid-8154 informational input: Stopped producing events.
    [smetj@indigo ~]$


Contents:

.. toctree::
    :maxdepth: 2

    installation
    introduction
    actor
    router
    modules
    bootstrap
    patterns

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`