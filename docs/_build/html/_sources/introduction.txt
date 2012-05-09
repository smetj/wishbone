============
Introduction
============

Wishbone is a gevent based framework to write `asynchronous`, modular message passing code by connecting message queues of multiple modules into a clean workflow.

Wishbone modules
================

Wishbone has a concept of modules. Each "Wishbone module" is a functionally isolated block of code which preferably does only 1 thing.
Each module has at least 2 queues called inbox and outbox.  The modules process data arriving in the "inbox" queue.  After consuming and processing the data, 
the module delivers it to its "outbox" queue.  The framework takes care of forwarding the content of this "outbox" to the queue of a module you connected it to.

By connecting the different queues with each other, one can make a clean "asynchronous" workflow in a simple way, without using any callbacks.

Wishbone comes with a some premade modules such as:

	* :class:`wishbone.io_modules.broker.Broker`
	* :class:`wishbone.io_modules.udpserver.UDPServer`
	* :class:`wishbone.modules.skeleton.Skeleton`
	* ...

Wishbone objects
================

Wishbone is organized around 2 objects which, in combination with "Wishbone Modules", can be combined into a data processing framework:

	* :class:`wishbone.wishbone.Wishbone`
	* :class:`wishbone.server.Server`

The Wishbone
------------

:class:`wishbone.wishbone.Wishbone` is the "root" class in which you register your modules and where you design your dataflow by interconnecting the queues of the
participating modules.















Multiple components are included:
    
    -   Wishbone() 
    
        A class with tools to register your components and to organize your workflow.

    -   PrimitiveActor()
    
        A baseclass which provide tools to write your own modules.
        
    -   Broker()
    
        An IO module which handles AMQP io.
        
    -   UDPServer()
    
        An IO module which accepts UDP data.
        
    -   Multiple data processing modules:
    
        To verify and convert json data, compress data, print data, ...
    
    


The data which is passed from one modules queue to another should have a certain format.  If not then it will be purged.
At a certain point you need to have a module which receives data from outside such as the Broker() or UDPServer() modules.


They are responsible to embed the raw data into the right format which is actually a dictionary with 2 elements, headers and data:

.. code-block:: python
    
    {'headers':{},'data':'your_data'}


Headers contains a dictionary with values for modules to use.  Data contains the actual data.
