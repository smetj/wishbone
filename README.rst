WishBone
========

What?
-----

A Python application framework and CLI tool build and manage async event
pipeline servers with minimal effort.

Example
-------

.. image:: docs/intro.png
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
