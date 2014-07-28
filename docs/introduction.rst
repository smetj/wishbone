============
Introduction
============

Wishbone is a Python library to create IO driven event processing servers by
defining a pipeline of inputs and outputs with a number of intermediate
processing stages through which events travel.

Wishbone comes with all the necessary tools and modules to bootstrap servers
from CLI and have them running as a permanent solution in a minimum of time.


Modules and Queues
------------------

Modules are isolated blocks of code (greenlets) each with their own specific
functionality. They are created by inheriting :py:class:`wishbone.Actor` as a
baseclass. Modules cannot (and are not supposed to) directly invoke each
others functionality. Their only means of interaction is by passing events to
each other's :py:class:`wishbone.Queue` queues. Modules typically have, but
are not limited to, an **inbox, outbox, successful** and **failed** queue.

Router
------

The :py:class:`wishbone.router.Default` plays an important role.  It's job is
to hold the initialized module instances and to organize the queue connections
between the different modules.

Modules are registered using
:py:func:`wishbone.router.Default.registerModule`. The router takes care of
the proper startup :py:func:`wishbone.router.Default.start` and shutdown
:py:func:`wishbone.router.Default.start` sequence of the registered modules.

The router automatically connects each module's *metrics* and *logs* queues to
a :py:class:`wishbone.module.Funnel` instance for your convenience.  This
allows the user to further organize log and metric processing.

Queues are connected to each other using
:py:func:`wishbone.router.Default.connect`.  Queues can only have a "1 to 1"
relationship.  If you require a "1 to N" you will have to use one of the
builtin flow modules.


Events
------

Wishbone events which travel from module to module are simple data structures:

.. code-block:: python

    { "header":{}, "data": object }

Input modules are responsible for creating events using this format.

Gevent
------

Wishbone uses Gevent.  The modules run as cooperatively scheduled greenlets
while taking advantage of the cooperative socket support for network IO.  This
makes Wishbone servers cope well with IO intensive tasks.
