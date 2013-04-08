WishBone
========

What?
-----

A Python library to write asynchronous event pipeline servers with minimal
effort.

How?
----

The WishBone Python library offers a framework to write asynchronous event
pipeline servers with minimal effort.  In this context, event pipelines are
best described as a collection of concurrently running modules which consume,
process and produce events. Wishbone module queues are connected to one
another forming a pipeline through which these events travel.  Wishbone
servers can be configured and controlled from from command line using
bootstrap files. Bootstrap files allow to cherry-pick Wishbone modules and to
define how events travel through them.  Multiple identical Wishbone instances
can run as separate processes offering parallel execution.

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
http://smetj.github.com/wishbone/docs/build/html/index.html

Examples
--------
https://github.com/smetj/experiments/tree/master/python/wishbone

Support
-------

Drop me an email or post a message on
https://groups.google.com/forum/?fromgroups#!forum/python-wishbone