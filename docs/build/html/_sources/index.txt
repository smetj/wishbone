==================================================================
 WishBone -- Write asynchronous event pipelines without callbacks.
==================================================================

Wishbone is a Python library to write `asynchronous` event pipelines without the need for callbacks.

In this context, "event pipelines" would be best described as a collection of isolated functions connected into a workflow through which events enter and exit to change along the way depending on which function they pass.  This is done by connecting modules to each other by shoveling data from one module's queue into the other in order to create an event pipeline. A module follows the Unix philosophy of writing programs that do one thing and do it well.  Modules work independently and asynchronously from each other without the need for callbacks.

WishBone is build upon the great Gevent library which uses the libevent library as an eventloop.

Download code from: https://github.com/smetj/wishbone

Download examples from: https://github.com/smetj/experiments/tree/master/python/wishbone

.. note::

   The documentation is work in progress.


Contents:

.. toctree::
   :maxdepth: 2

   introduction
   module
   modules
   io_modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. todolist::
