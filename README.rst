WishBone
========

What?
-----

A Python library and CLI tool to build and manage event pipeline servers with
minimal effort.

Example
-------

.. image:: docs/intro.png
    :align: center

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


Installing
----------

Through Pypi:

	$ easy_install wishbone

Or the latest development branch from Github:

	$ git clone git@github.com:smetj/wishbone.git

	$ cd wishbone

	$ sudo python setup.py install


Documentation
-------------

https://wishbone.readthedocs.org/en/latest/index.html


Modules
-------

https://github.com/smetj/wishboneModules

Support
-------

Drop me an email or post a message on:

https://groups.google.com/forum/?fromgroups#!forum/python-wishbone
