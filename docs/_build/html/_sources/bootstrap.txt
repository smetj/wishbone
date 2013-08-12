===================
Bootstraping on CLI
===================

Wishbone comes with a CLI tool to easily bootstrap a server using a YAML
formatted config file.  Following file creates exactly the same environment as
the above example:

.. literalinclude:: examples/test_setup.yaml
   :language: yaml

Bootstrapping the environment is just a matter of invoking the **wishbone**
executable with the --config parameter pointing to the bootstrap file.


Available commands
==================

start
-----

The start command detaches the Wishbone server from console and runs it in the
background.  This implies that logs are written to syslog unless specifically
defined otherwise.  Metrics are written to Null unless specifically defined
otherwise.

The pidfile contains the pids of the control process and all child processes.
When stopping a Wishbone instance make sure you point to the pid file used to
start the Wishbone instance.


.. code-block:: none

    [smetj@indigo ~]$ wishbone start -h
    usage: wishbone start [-h] [--config CONFIG] [--instances INSTANCES]
                          [--pid PID]

    Starts a Wishbone instance and detaches to the background. Logs are written to
    syslog.

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       The Wishbone bootstrap file to load.
      --instances INSTANCES
                            The number of parallel Wishbone instances to
                            bootstrap.
      --pid PID             The pidfile to use.


------------------

debug
-----

The debug command does pretty much the same as start just that it keeps the
Wishbone instance in the foreground without detaching it.  Logs are written to
STDOUT.  The running instance can be stopped gracefully with CTRL+C

.. code-block:: none

    [smetj@indigo ~]$ wishbone debug -h
    usage: wishbone debug [-h] [--config CONFIG] [--instances INSTANCES]

    Starts a Wishbone instance in foreground and writes logs to STDOUT.

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       The Wishbone bootstrap file to load.
      --instances INSTANCES
                            The number of parallel Wishbone instances to
                            bootstrap.


------------------

stop
----

Stops the Wishbone instance gracefully by sending SIGINT to all processes.

.. code-block:: none

    smetj@indigo ~]$ wishbone stop -h
    usage: wishbone stop [-h] [--pid PID]

    Tries to gracefully stop the Wishbone instance.

    optional arguments:
      -h, --help  show this help message and exit
      --pid PID   The pidfile to use.


------------------

kill
----

** Use with caution, sends SIGKILL to the pids in the pidfile. **

.. code-block:: none

    [smetj@indigo ~]$ wishbone kill -h
    usage: wishbone kill [-h] [--pid PID]

    Kills the Wishbone processes immediately.

    optional arguments:
      -h, --help  show this help message and exit
      --pid PID   The pidfile to use.


------------------

list
----

Lists all installed Wishbone modules, given that they have the correct entry-points.

.. code-block:: none

    [smetj@indigo ~]$ wishbone list
    Available Wishbone modules:
    +---------------------------+-------------------+------------------------------------------------------------------------------------------+
    | Group                     | Module            | Description                                                                              |
    +---------------------------+-------------------+------------------------------------------------------------------------------------------+
    | wishbone.builtin.logging  | loglevelfilter    | A builtin Wishbone module which filters Wishbone log events.                             |
    |                           | humanlogformatter | A builtin Wishbone module which formats Wishbone log events.                             |
    |                           |                   |                                                                                          |
    | wishbone.builtin.metrics  | graphite          | A builtin Wishbone module which formats the internal metric format into Graphite format. |
    |                           |                   |                                                                                          |
    | wishbone.builtin.flow     | roundrobin        | A builtin Wishbone module which round robins incoming events                             |
    |                           |                   |     over all connected queues.                                                           |
    |                           | fanout            | A builtin Wishbone module which duplicates incoming events to all                        |
    |                           |                   |     connected queues.                                                                    |
    |                           | tippingbucket     | A builtin Wishbone module which buffers data.                                            |
    |                           | funnel            | A builtin Wishbone module which merges incoming events from different                    |
    |                           |                   |     queues into 1 queue.                                                                 |
    |                           | lockbuffer        | A builtin Wishbone module with a fixed size inbox queue.                                 |
    |                           |                   |                                                                                          |
    | wishbone.builtin.function | header            |  A builtin Wishbone module which adds the defined dictionary                             |
    |                           |                   |     to the header of each passing event.                                                 |
    |                           |                   |                                                                                          |
    | wishbone.builtin.input    | testevent         | A WishBone input module which generates a test event at the chosen interval.             |
    |                           |                   |                                                                                          |
    | wishbone.builtin.output   | syslog            | Writes Wishbone log events to syslog.                                                    |
    |                           | null              | Accepts events and purges these without any further processing.                          |
    |                           | stdout            | A builtin Wishbone module prints events to STDOUT.                                       |
    |                           |                   |                                                                                          |
    | wishbone.input            | dictgenerator     | A WishBone input module which generates dictionaries build out of words randomly         |
    |                           |                   |     chosen from a provided wordlist.                                                     |
    |                           | amqp              | A Wishbone AMQP input module.                                                            |
    |                           | gearman           | A Wishbone input module which consumes jobs from a Gearmand server.                      |
    |                           | generator         | A WishBone IO module which generates random data for testing purposes.                   |
    |                           | namedpipe         | A Wishbone IO module which accepts external input from a named pipe.                     |
    |                           | tcp               | A Wishbone input module which listens on a TCP socket.                                   |
    |                           | udp               | A Wishbone module which handles UDP input.                                               |
    |                           | uds               | A Wishbone input module which listens on a unix domain socket.                           |
    |                           | mongodb           | A Wishbone output module to write data in MongoDB.                                       |
    |                           |                   |                                                                                          |
    | wishbone.output           | amqp              | A Wishbone AMQP output module.                                                           |
    |                           | tcp               | A Wishbone IO module which writes data to a TCP socket.                                  |
    |                           | uds               | A Wishbone IO module which writes data to a Unix domain socket.                          |
    |                           |                   |                                                                                          |
    | wishbone.function         | skeleton          | A bare minimum Wishbone function module.                                                 |
    |                           | msgpack           | A Wishbone which de/serializes data into or from msgpack format.                         |
    |                           | snappy            | A Wishbone module which compresses or decompresses data using Snappy.                    |
    |                           | json              | A Wishbone module which converts and validates JSON.                                     |
    |                           | waitseconds       | An output module which takes x seconds to finish the <consume> function.                 |
    |                           |                   |                                                                                          |
    +---------------------------+-------------------+------------------------------------------------------------------------------------------+

------------------

show
----

Displays the docstring of the requested module.


.. code-block:: none

    [smetj@indigo ~]$ wishbone show wishbone.builtin.flow.fanout
    **A builtin Wishbone module which duplicates incoming events to all
        connected queues.**

        Create a "1 to n" relationship with queues.  Events arriving in inbox
        are then copied to each queue connected to this module.  Keep in mind
        that the outbox queue is never used.

        When clone is True, each incoming event is duplicated for each outgoing
        queue.  This might be usefull if you require to change the content of the
        events later down the pipeline.  Otherwise references are used which means
        changing the event will change it everywhere in the current Wishbone
        framework.


        Parameters:

            name(str):      The name of the module.

            clone(bool):    When True actually makes a copy instead of passing
                            a reference.

        Queues:

            inbox:  Incoming events


