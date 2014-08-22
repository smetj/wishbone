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


.. code-block:: sh

    [smetj@indigo ~]$ wishbone start -h
    usage: wishbone start [-h] [--config CONFIG] [--instances INSTANCES]
                          [--pid PID] [--queue-size QUEUE_SIZE]
                          [--frequency FREQUENCY] [--id IDENT]

    Starts a Wishbone instance and detaches to the background. Logs are written to
    syslog.

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       The Wishbone bootstrap file to load.
      --instances INSTANCES
                            The number of parallel Wishbone instances to
                            bootstrap.
      --pid PID             The pidfile to use.
      --queue-size QUEUE_SIZE
                            The queue size to use.
      --frequency FREQUENCY
                            The metric frequency.
      --id IDENT            An identification string.


------------------

debug
-----

The debug command does pretty much the same as start just that it keeps the
Wishbone instance in the foreground without detaching it.  Logs are written to
STDOUT.  The running instance can be stopped gracefully with CTRL+C

.. code-block:: sh

    [smetj@indigo ~]$ wishbone debug -h
    usage: wishbone debug [-h] [--config CONFIG] [--instances INSTANCES]
                          [--queue-size QUEUE_SIZE] [--frequency FREQUENCY]
                          [--id IDENT]

    Starts a Wishbone instance in foreground and writes logs to STDOUT.

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       The Wishbone bootstrap file to load.
      --instances INSTANCES
                            The number of parallel Wishbone instances to
                            bootstrap.
      --queue-size QUEUE_SIZE
                            The queue size to use.
      --frequency FREQUENCY
                            The metric frequency.
      --id IDENT            An identification string.


------------------

stop
----

Stops the Wishbone instance gracefully by sending SIGINT to all processes.

.. code-block:: sh

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

.. code-block:: sh

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

.. code-block:: sh

    [smetj@indigo ~]$ wishbone list
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


------------------

show
----

Displays the docstring of the requested module.


.. code-block:: sh

    [smetj@indigo ~]$ wishbone show --module wishbone.flow.fanout
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 0.5.0

    Build event pipeline servers with minimal effort.



    ====================
    wishbone.flow.fanout
    ====================

    Version: 0.5.0

    Funnel multiple incoming queues to 1 outgoing queue.
    ----------------------------------------------------


        Funnel multiple incoming queues to 1 outgoing queue.

        Parameters:

            - name(str)
               |  The name of the module.

            - size(int)
               |  The default max length of each queue.

            - frequency(int)
               |  The frequency in seconds to generate metrics.

            - dupe(bool)(False)
               |  Determines whether we send references to the
                  original event to all destination or an
                  actual copy.


        Queues:

            outbox
             |  Outgoing events.