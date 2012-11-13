============
Introduction
============

Wishbone is a Python programming library to write `asynchronous` event pipelines mainly focussed on event processing.
It does this by connecting modules to each other by shoveling data from one module's queue into the other in order to create an event processing flow.
A module follows the Unix philosophy of writing programs that do one thing and do it well.  Modules work independently and asynchronously from each other without the need for callbacks.
WishBone is build upon the great Gevent library which uses the libevent library as an eventloop.

Wishbone modules
================

Wishbone has a concept of modules. Each "Wishbone module" is a functionally isolated block of code which preferably does only 1 thing.
Each module has at least 2 queues called inbox and outbox.  The modules process data arriving in the "inbox" queue.  After consuming and processing the data, 
the module delivers it to its "outbox" queue.  The framework takes care of forwarding the content of this "outbox" to the inbox queue of a module you connected it to.

By connecting the different queues with each other, one can make a clean "asynchronous" workflow in a simple way, without using any callbacks.

There are 2 types of modules:
    IO_modules receive/submit messages from/to outside the Wishbone framework.
    Modules receive/submit message to other modules.

Wishbone
========

Wishbone is organized around 1 object which, holds and organises the chain of Wishbone modules resulting into your processing workflow.

	* :class:`wishbone.main.Wishbone`

The data which is passed from one modules queue to another should have a certain format.  If not then it will be purged.
At a certain point you need to have a module which receives data from outside such as the Broker() or UDPServer() modules.

They are responsible to embed the raw data into the right format which is actually a dictionary with 2 elements, headers and data:

.. code-block:: python
    
    {'headers':{},'data':'your_data'}


Headers contains a dictionary with values for modules to use.  Data contains the actual data.


ParallelServer
==============

ParallelServe is a class which allows you to start multiple Wishbone event pipelines in parallel each as a different process.
This basically results into a libevent loop per process.

	* :class:`wishbone.server.ParallelServer`
