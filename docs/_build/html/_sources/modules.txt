=======
Modules
=======

Wishbone comes with a set of builtin modules.  Modules are isolated blocks of
functionality which are connected to each other within a router instance.

There are different types of modules:

    - input modules
    - output modules
    - flow modules
    - function modules

Besides the builtin modules there is also a list modules which are developed
and maintained apart from Wishbone.  They include tcp/udp servers and clients,
amqp client, etc ...

https://github.com/smetj/wishboneModules


Input modules
-------------

Input modules take input from the outside world into the Wishbone framework.
They often have only 1 :class:`wishbone.tools.WishboneQueue` called **outbox**
in which incoming events go. Input modules are also responsible to format any
incoming data into the expected Wishbone internal event format.

--------

TestEvent
*********
.. autoclass:: wishbone.module.TestEvent

--------

Output modules
--------------

Output modules take input from another module registered in the Wishbone
router and submit these events to the outside world. They often have only 1
:class:`wishbone.tools.WishboneQueue` called **inbox** in which events arrive
destined to go out. They typically act as TCP, AMQP or other network protocol
clients.

--------

Syslog
******
.. autoclass:: wishbone.module.Syslog

--------

Null
****
.. autoclass:: wishbone.module.Null

--------

STDOUT
******
.. autoclass:: wishbone.module.STDOUT

--------

Flow modules
------------

Flow modules accept and forward events from and to other modules.  They
fulfill a key roll in building a message flow.  Since you can only have a 1:1
relationship between queues, you cannot split or merge event streams.  That's
where flow modules come handy.  Flow modules are not expected to alter events
when transiting the module.

--------

RoundRobin
**********
.. autoclass:: wishbone.module.RoundRobin

--------

Fanout
******
.. autoclass:: wishbone.module.Fanout

--------

Funnel
******
.. autoclass:: wishbone.module.Funnel

--------

TippingBucket
*************
.. autoclass:: wishbone.module.TippingBucket

--------

LockBuffer
**********
.. autoclass:: wishbone.module.LockBuffer

--------

Function modules
----------------

Function modules accept and forward events from and to other modules.  They
can have a wide range of functionality and change events when transiting the
module.

--------

Header
******
.. autoclass:: wishbone.module.Header

--------

Logging modules
---------------

The logging modules are a specialized set of modules meant to process the logs
produced by the modules and collected by the router.

--------

humanlogformatter
*****************
.. autoclass:: wishbone.module.HumanLogFormatter

--------

Loglevelfilter
**************
.. autoclass:: wishbone.module.LogLevelFilter

--------


Metrics modules
---------------

The metrics modules are a specialized set of modules meant to process the
metrics produced by the modules and collected by the router.

--------

graphite
********
.. autoclass:: wishbone.module.Graphite

--------