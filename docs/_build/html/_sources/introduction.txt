============
Introduction
============

Wishbone is a Python library to create IO driven event processing servers by
defining a pipeline of inputs and outputs with a number of intermediate
processing stages in between through which events travel.

It also provides the tools to quickly bootstrap and control event pipeline
setups from CLI and have them running as permanent solutions.


Modules and Queues
------------------

Modules are isolated blocks of code (greenlets) each with their own specific
functionality. They are created by simply inheriting
:py:class:`wishbone.Actor` as a baseclass. Modules cannot directly invoke each
others functionality. Their only means of interaction is by passing messages
or events to each other's :py:class:`wishbone.tools.WishboneQueue` queues.
Modules typically have, but are not limited to, an inbox and outbox queue.

Queues always live inside a :py:class:`wishbone.tools.QueuePool` which,
besides offering some convenience functions, is nothing more than a container
to centralize all the queues of the module. Typically, modules consume each
event entering the inbox queue using the :py:func:`wishbone.Actor.consume`
function where the event can be processed and after which it is submitted to
the module's outbox queue from where it can be forwarded again to another
module's queue.

Besides a selection of builtin modules which deliver core Wishbone
functionality, there is also a collection of modules which are maintained as a
separate project. The modules can be found on
https://github.com/smetj/wishboneModules.


Router
------

The :py:class:`wishbone.router.Default` router is used to initialize the
modules and to organize the event stream between them.

Modules are registered using :py:func:`wishbone.router.Default.register`. The
router takes care of the proper startup
:py:func:`wishbone.router.Default.start` and shutdown
:py:func:`wishbone.router.Default.start` sequence of all the modules.

Queues are connected to each other using
:py:func:`wishbone.router.Default.connect`.  Queues can only have a "1 to 1"
relationship.  If you require a "1 to N" or similar scenario you might have to
use one of the builtin flow modules.

The router also takes care of the logs and metrics produced by the modules.
By registering Wishbone modules using
:py:func:`wishbone.router.Default.registerLogModule` and
:py:func:`wishbone.router.Default.registerMetricModule` we can pretty much do
what we want with them.

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
