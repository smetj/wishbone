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

Works on python 2.6+, 2.7+ including Python 3 and PyPy 2.0.2

.. image:: intro.png
    :align: right

.. code-block:: python

    >>> from wishbone.router import Default
    >>> from wishbone.module import TestEvent
    >>> from wishbone.module import RoundRobin
    >>> from wishbone.module import STDOUT
    >>>
    >>> router=Default()
    >>> router.register(TestEvent, "input")
    >>> router.register(RoundRobin, "mixing")
    >>> router.register(STDOUT, "output1", prefix="I am number one: ")
    >>> router.register(STDOUT, "output2", prefix="I am number two: ")
    >>>
    >>> router.connect("input.outbox", "mixing.inbox")
    >>> router.connect("mixing.one", "output1.inbox")
    >>> router.connect("mixing.two", "output2.inbox")
    >>>
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
roundrobins the incoming events to 2 :class:`wishbone.module.STDOUT` module
instances which print all incoming events to STDOUT.


Bootstrapping
=============

Wishbone comes with a CLI tool to easily bootstrap a server using a YAML
formatted config file.  Following file creates exactly the same environment as
the above example:

.. literalinclude:: examples/test_setup.yaml
   :language: yaml

Bootstrapping the environment is just a matter of invoking the **wishbone**
executable with the --config parameter pointing to the bootstrap file.

.. code-block:: sh

    [smetj@indigo ~]$ wishbone debug --config test.yaml
    2013-08-09T23:13:39 pid-13797 informational Router: Queue one does not exist in module mixing.  Autocreate queue.
    2013-08-09T23:13:39 pid-13797 informational Router: Queue two does not exist in module mixing.  Autocreate queue.
    2013-08-09T23:13:39 pid-13797 informational Router: Starting.
    2013-08-09T23:13:39 pid-13797 informational loglevelfilter: Initiated
    2013-08-09T23:13:39 pid-13797 informational loglevelfilter: Created module queue named inbox with max_size 0.
    2013-08-09T23:13:39 pid-13797 informational loglevelfilter: Created module queue named outbox with max_size 0.
    ... snip ...
    2013-08-09T23:13:39 pid-13797 informational input: Started
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    I am number two: test
    I am number one: test
    ^C2013-08-09T23:13:47 pid-13797 informational Router: Received SIGINT. Shutting down.
    2013-08-09T23:13:47 pid-13797 informational Router: Stopping.
    2013-08-09T23:13:47 pid-13797 informational output2: Shutdown
    2013-08-09T23:13:48 pid-13797 warning output2: Queue <wishbone.tools.wishbonequeue.WishboneQueue instance at 0x2101a28> locked.
    2013-08-09T23:13:48 pid-13797 informational output1: Shutdown
    2013-08-09T23:13:48 pid-13797 warning output1: Queue <wishbone.tools.wishbonequeue.WishboneQueue instance at 0x2101680> locked.
    2013-08-09T23:13:48 pid-13797 informational mixing: Shutdown
    2013-08-09T23:13:48 pid-13797 warning mixing: Queue <wishbone.tools.wishbonequeue.WishboneQueue instance at 0x2101098> locked.
    2013-08-09T23:13:49 pid-13797 informational input: Shutdown
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