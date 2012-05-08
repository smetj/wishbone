============
Introduction
============

Wishbone is a gevent based framework to write `asynchronous`, modular message passing code by connecting local message queues of multiple modules into a clean workflow.

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
    
    
The idea is that each "Wishbone module" plugged into the framework has a consume() function.  This function consumes all messages from the module's inbox, 
processes them and puts them back into the outbox queue.  By connecting the in- and outbox queues of all modules you create a clear modular data flow.


The data which is passed from one modules queue to another should have a certain format.  If not then it will be purged.
At a certain point you need to have a module which receives data from outside such as the Broker() or UDPServer() modules.


They are responsible to embed the raw data into the right format which is actually a dictionary with 2 elements, headers and data:

.. code-block:: python
    
    {'headers':{},'data':'your_data'}


Headers contains a dictionary with values for modules to use.  Data contains the actual data.
