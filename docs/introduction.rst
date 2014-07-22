============
Introduction
============

Wishbone is a Python library to create IO driven event processing servers by
defining a pipeline of inputs and outputs with a number of intermediate
processing stages in between through which events travel.

It comes with all the necessary tools and modules to bootstrap a processing
server from CLI and have it running as a permanent solution in a minimum of
time.


Modules and Queues
------------------

Modules are isolated blocks of code (greenlets) each with their own specific
functionality. They are created by having a class inherit
:py:class:`wishbone.Actor` as a baseclass. Modules cannot (and are not
supposed to) directly invoke each others functionality. Their only means of
interaction is by passing events to each other's
:py:class:`wishbone.Queue` queues. Modules typically have, but are not limited
to, an inbox, outbox, successful and failed queue.

Router
------

The :py:class:`wishbone.router.Default` router is used to initialize the
modules and to organize the event stream between them.

Modules are registered using
:py:func:`wishbone.router.Default.initializeModule`. The router takes care of
the proper startup :py:func:`wishbone.router.Default.start` and shutdown
:py:func:`wishbone.router.Default.start` sequence of all the modules.

Queues are connected to each other using
:py:func:`wishbone.router.Default.connect`.  Queues can only have a "1 to 1"
relationship.  If you require a "1 to N" or similar scenario you might have to
use one of the builtin flow modules.


Events
------

Wishbone events are simple data structures which need to have following format:

.. code-block:: python

    { "header":{}, "data": object }

Input modules are responsible to create events with the correct format from
the incoming data.  Events which do not comply with this format are discarded.

Gevent
------

Wishbone is build using Gevent.  The modules are running as cooperatively
scheduled greenlets while taking advantage of the cooperative socket support
for network IO.
