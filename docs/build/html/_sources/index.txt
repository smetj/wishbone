==========
 WishBone 
==========
 
**A Python library to easily write coroutine based event pipeline solutions.**

In this context, "event pipelines" would be best described as a collection of isolated functions connected into a workflow through which events travel and change.
This is done by shoveling events from one module's queue into the other in order to create a "flow-chart like" event pipeline. A Wishbone module follows the Unix philosophy of writing programs that do one thing and do it well. Within a Wishbone instance, the modules are running pseudo-concurrently using greenlets on top of a libevent event loop thanks to the the great Gevent library.  Wishbone also offers the possibility to start multiple concurrent processes each with a Wishbone (libevent) instance.

Download code from: https://github.com/smetj/wishbone

Download examples from: https://github.com/smetj/experiments/tree/master/python/wishbone

.. note::

   WishBone requires gevent > 1.0 


Contents:

.. toctree::
   :maxdepth: 2

   introduction
   bootstrapfiles
   iomodules
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. todolist::
