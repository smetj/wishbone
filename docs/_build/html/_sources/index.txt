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

Wishbone is a gevent based framework which simplifies writing modular message passing code. It allows you to build a data flow by connecting the in- and outbox queue of multiple modules. 
The goal is that each module has (at least) an inbox and outbox queue. Each module has a consume() function, which is consumes all messages from the inbox queue.
It’s up to the consume() function to put the data into the outbox queue.  A programmer connects the outbox of one module to the inbox of another in order to create a dataflow. 


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


