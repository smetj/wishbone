.. Wishbone documentation master file, created by
   sphinx-quickstart on Tue May  1 11:41:22 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Wishbone 
====================================

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

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



Example
======= 

Let's make a simple program which consumes data from an AMQP messagebroker, prints it to STDOUT and writes the data back into the broker.

The Wishbone framework comes with modules such as the io_module "Broker" and the module "STDOUT".
The Broker module consumes and produces data to a message broker infrastructure, while the STDOUT module merely prints messages from its inbox and then puts those messages back into outbox.

.. code-block:: python
    :linenos:
    
    #!/usr/bin/python

    import wishbone
    from wishbone.toolkit import PrimitiveActor

    class Header(PrimitiveActor):
        def __init__(self, name, *args, **kwargs):
            PrimitiveActor.__init__(self, name)
        def consume(self,message):
            message['header']['broker_exchange'] = ''
            message['header']['broker_key'] = 'test'
            self.outbox.put(message)

    wb = wishbone.Wishbone()
    wb.registerModule ( ('wishbone.io_modules', 'Broker', 'broker'), host='sandbox', vhost='/', username='guest', password='guest', consume_queue='indigo' )
    wb.registerModule ( ('wishbone.modules', 'STDOUT', 'stdout') )
    wb.registerModule ( ('__main__', 'Header', 'header') )

    wb.connect (wb.broker.inbox, wb.stdout.inbox)
    wb.connect (wb.stdout.outbox, wb.header.inbox)
    wb.connect (wb.header.outbox, wb.broker.inbox)

    wb.start()

-   lines 15,16,17 we register our modules in the Wishbone class.
-   lines 19,20 and 21 we connect the queues defining the actual dataflow.

The Header class is a Wishbone module created from scratch by inheriting the PrimitiveActor baseclass.
When this baseclass is inherited, the modules automatically gets an inbox and outbox queue.
For each message arriving in the inbox queue, the consume() function is called.  In this function we modify the header with extra information.
This allows the Broker module to route messages using a specific exchange and or routing key.

And that's it!


Wishbone Class
==============

.. automodule:: wishbone.wishbone
   :members:

Toolkit Class
==============

.. automodule:: wishbone.toolkit
   :members:

Skeleton Class
==============

.. automodule:: wishbone.modules.skeleton
   :members:

Jsonvalidator Class
===================

.. automodule:: wishbone.modules.jsonvalidator
   :members:

Compressor Class
================
.. automodule:: wishbone.modules.compressor
   :members:

STDOUT Class
================

.. automodule:: wishbone.modules.stdout
   :members:

Broker Class
============

.. automodule:: wishbone.io_modules.broker
   :members:

UDPserver Class
===============

.. automodule:: wishbone.io_modules.udpserver
   :members:


