================
Wishbone modules
================

Introduction
------------

Modules are isolated blocks of code (greenlets) each with their own specific
functionality. They are created by inheriting :py:class:`wishbone.Actor` as a
baseclass. Modules cannot (and are not supposed to) directly invoke each
others functionality. Their only means of interaction is by passing events to
each other's :py:class:`wishbone.Queue` queues. Modules typically have, but
are not limited to, an **inbox, outbox, success** and **failed** queue.

A module's queues always live inside :py:class:`wishbone.QueuePool` which,
besides offering some convenience functions, is nothing more than a container
to centralize all the module's queues. Typically, modules consume the events
entering the *inbox* queue and apply to them to some pre-registered method.
Registering a method to consume all events of a queue is done using
:py:class:`wishbone.Actor.registerConsumer`.  The registered method is then
responsible to submit the event to another queue of choice, typically but not
necessarily *outbox*.


Module categories
-----------------

Modules are stored into a hierarchical name space.  The name of a module
consists out of:

*<category name> . <group name> . <module name>*

Wishbone comes with a set of builtin modules which are an integral part of the
Wishbone framework.

External modules are installed as regular Python modules and should create an
entrypoint in the *wishbone.contrib* namespace.

https://github.com/smetj/wishboneModules is a repository containing additional
modules.


You can list all available modules using the *list* command:

.. code-block:: sh

    $ wishbone list
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 0.5.0

    Build event pipeline servers with minimal effort.


    Available modules:
    +----------+----------+----------------+---------+------------------------------------------------------------+
    | Category | Group    | Module         | Version | Description                                                |
    +----------+----------+----------------+---------+------------------------------------------------------------+
    |          |          |                |         |                                                            |
    | wishbone | flow     | funnel         |   0.5.0 | Funnel multiple incoming queues to 1 outgoing queue.       |
    |          |          | fanout         |   0.5.0 | Funnel multiple incoming queues to 1 outgoing queue.       |
    |          |          | roundrobin     |   0.5.0 | Round-robins incoming events to all connected queues.      |
    |          |          |                |         |                                                            |
    |          | encode   | humanlogformat |   0.5.0 | Formats Wishbone log events.                               |
    |          |          | msgpack        |   0.5.0 | Encodes events to MSGPack format.                          |
    |          |          | graphite       |   0.5.0 | Converts the internal metric format to Graphite format.    |
    |          |          |                |         |                                                            |
    |          | decode   | msgpack        |   0.5.0 | Decodes events from MSGPack format.                        |
    |          |          |                |         |                                                            |
    |          | function | header         |   0.5.0 | Adds information to event headers.                         |
    |          |          |                |         |                                                            |
    |          | input    | amqp           |   0.5.0 | Consumes messages from AMQP.                               |
    |          |          | testevent      |   0.5.0 | Generates a test event at the chosen interval.             |
    |          |          | tcp            |   0.5.0 | A Wishbone input module which listens on a TCP socket.     |
    |          |          | subscriber     |   0.5.0 | Subscribes to one or more ZeroMQ publishers.               |
    |          |          | dictgenerator  |   0.5.0 | Generates random dictionaries.                             |
    |          |          | disk           |   0.5.0 | Reads messages from a disk buffer.                         |
    |          |          |                |         |                                                            |
    |          | output   | publisher      |   0.5.0 | Publishes data to one or more ZeroMQ receivers.            |
    |          |          | null           |   0.5.0 | Purges incoming events.                                    |
    |          |          | amqp           |   0.5.0 | Produces messages to AMQP.                                 |
    |          |          | stdout         |   0.5.0 | Prints incoming events to STDOUT.                          |
    |          |          | tcp            |   0.5.0 | A Wishbone ouput module which writes data to a TCP socket. |
    |          |          | syslog         |   0.5.0 | Writes log events to syslog.                               |
    |          |          | disk           |   0.5.0 | Writes messages to a disk buffer.                          |
    |          |          |                |         |                                                            |
    +----------+----------+----------------+---------+------------------------------------------------------------+



To read the help and module instructions use the **show** command:

.. code-block:: sh

    $ wishbone show --module wishbone.input.testevent
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 0.5.0

    Build event pipeline servers with minimal effort.



    ========================
    wishbone.input.testevent
    ========================

    Version: 0.5.0

    Generates a test event at the chosen interval.
    ----------------------------------------------



        Events have following format:

            { "header":{}, "data":"test" }

        Parameters:

            - name(str)
               |  The name of the module.

            - size(int)
               |  The default max length of each queue.

            - frequency(int)
               |  The frequency in seconds to generate metrics.

            - interval(float)(1)
               |  The interval in seconds between each generated event.
               |  A value of 0 means as fast as possible.

            - message(string)("test")
               |  The content of the test message.

            - numbered(bool)
               |  When true, appends a sequential number to the end.


        Queues:

            - outbox
               |  Contains the generated events.




Module groups
-------------

Wishbone modules are divided into 6 group types depending on their
functionality:

input modules
~~~~~~~~~~~~~

Input modules take input from the outside into the Wishbone framework.  They
are responsible of accepting data and converting that data into the
appropriate Wishbone data format.  Input modules typically have a
:py:class:`wishbone.Queue` named *output*.

output modules
~~~~~~~~~~~~~~

Output modules are responsible for submitting Wishbone event data to the
outside world.  Output modules typically have a :py:class:`wishbone.Queue`
named *input*.

flow modules
~~~~~~~~~~~~

Flow modules do not change data but they decide on the flow of events in the
pipeline.

function modules
~~~~~~~~~~~~~~~~

Function modules can have a wide range of functionalities but they take events
in, change them and send events out.  Function modules have at least 1
incoming and 1 outgoing queue.

encode modules
~~~~~~~~~~~~~~

Encode a data format into another or into the internal metric/log format.

decode modules
~~~~~~~~~~~~~~

Decode a data format into another or into the internal metric/log format.


Important properties and behavior
---------------------------------

success and failed queues
~~~~~~~~~~~~~~~~~~~~~~~~~

Each module has a *success* and *failed* queue.  Whenever a registered
method (see :py:class:`wishbone.Actor.registerConsumer`) fails to process an
event, the framework will submit the event into the *failed* queue.  Therefor
it is important not to trap exceptions in the *registered consumer methods*
but rather rely upon the fact Wishbone will trap that exception and submits it
to the *failed* queue from which it can be further processed by another
module.

An example which takes advantage of this behavior might be connecting the
*failed* queue of the :py:class:`wishbone.module.TCPOut` module to the *inbox*
queue of the :py:class:`wishbone.module.DiskOut` module.

On the other side, each time a *registered consumer method* successly
processes an event, it will automatically be submitted to the *success*
queue, from where it can be further processed by another module when desired.

An example which takes advantage of this behavior might be connecting the
*success* queue of the :py:class:`wishbone.module.TCPOut` module to the
*acknowledgment* queue of the :py:class:`wishbone.module.AMQPOut` module.

It's up to the method which has been registered to consume a queue to submit
the event to another queue such as *outbox* from where it can be routed to the
next module for further processing.

metrics and logs queues
~~~~~~~~~~~~~~~~~~~~~~~

Each module has a *metrics* and *logs* queue which hold metric and log events
respectively, ready to be consumed by another module.  If these queues aren't
connected to other queues then that data will be dropped.


Queues drop data by default
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a queue is not connected it will drop all messages submitted to it.  The
moment a queue is connected to another queue, messages are kept and
transported.

Module default parameters
~~~~~~~~~~~~~~~~~~~~~~~~~

The :py:class:`wishbone.Actor` baseclass must be initialized with a
:py:class:`wishbone.actor.ActorConfig` module, which requires 3 parameters.

.. autoclass:: wishbone.actor.ActorConfig

- name: The name of the module.
- size: The size of each of the module queues.
- frequency: The frequency at which metrics are generated.

Events
------

Events are very simple *<type 'dict'>* data structures which contain a
*header* and a *data* key.

The *header* is a again a *<type 'dict'>* while, *data* can be any type of
object.

.. code-block:: python

    { "header":{}, "data": object }


Example
-------

Consider following example module which reverses the content of incoming
events and optionally converts the first letter into a capital.

.. literalinclude:: examples/reversedata.py
   :language: python
   :linenos:

--------

- The ReverseData class inherits the :py:class:`wishbone.Actor` base class[4].
- The :py:class:`wishbone.Actor` base class is initialized with name,
  size and frequency parameter [23].
- Two queues, inbox and outbox are created [24][25].
- The *consume* method [36] is registered to consume each event from the
  *inbox* queue using the :py:class:`wishbone.Actor.registerConsumer`
  method[26].
- The *preHook* [30] method is executed before starting the registered
  consumer methods while the the *postHook* [33] method is executed before
  shutdown. They are invoked automatically by the Wishbone framework.
- Logging is done by simply invoking the appropriate
  :py:class:`wishbone.Logging` functions.
- The registered consumer method is responsible for adding the (changed) event
  to the appropriate queue. [46]
