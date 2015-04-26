======
Server
======

**start**

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
                          [--frequency FREQUENCY] [--id IDENTIFICATION]

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
      --id IDENTIFICATION   An identification string.

------------------

**debug**

The debug command does pretty much the same as start just that it keeps the
Wishbone instance in the foreground without detaching it.  Logs are written to
STDOUT.  The running instance can be stopped gracefully with CTRL+C

.. code-block:: sh

    [smetj@indigo ~]$ wishbone debug -h
    usage: wishbone debug [-h] [--config CONFIG] [--instances INSTANCES]
                          [--queue-size QUEUE_SIZE] [--frequency FREQUENCY]
                          [--id IDENTIFICATION]

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
      --id IDENTIFICATION   An identification string.

------------------

**stop**

Stops the Wishbone instance gracefully by sending SIGINT to all processes.

.. code-block:: sh

    smetj@indigo ~]$ wishbone stop -h
    usage: wishbone stop [-h] [--pid PID]

    Tries to gracefully stop the Wishbone instance.

    optional arguments:
      -h, --help  show this help message and exit
      --pid PID   The pidfile to use.


------------------

**kill**

** Use with caution, sends SIGKILL to the pids in the pidfile. **

.. code-block:: sh

    [smetj@indigo ~]$ wishbone kill -h
    usage: wishbone kill [-h] [--pid PID]

    Kills the Wishbone processes immediately.

    optional arguments:
      -h, --help  show this help message and exit
      --pid PID   The pidfile to use.

------------------

**list**

Lists all installed Wishbone modules, given that they have the correct entry-points.

.. code-block:: sh

    [smetj@indigo ~]$ wishbone list
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 1.1.0

    Build event pipeline servers with minimal effort.

    Available modules:
    +----------+----------+----------------+---------+----------------------------------------------------------------------------+
    | Category | Group    | Module         | Version | Description                                                                |
    +----------+----------+----------------+---------+----------------------------------------------------------------------------+
    |          |          |                |         |                                                                            |
    | wishbone | flow     | fanout         |   1.1.0 | Forward each incoming message to all connected queues.                     |
    |          |          | funnel         |   1.1.0 | Funnel multiple incoming queues to 1 outgoing queue.                       |
    |          |          | match          |   1.1.0 | Pattern matching on a key/value document stream.                           |
    |          |          | roundrobin     |   1.1.0 | Round-robins incoming events to all connected queues.                      |
    |          |          |                |         |                                                                            |
    |          | encode   | graphite       |   1.1.0 | Converts the internal metric format to Graphite format.                    |
    |          |          | humanlogformat |   1.1.0 | Formats Wishbone log events.                                               |
    |          |          | json           |   1.1.0 | Encodes Python data objects to JSON strings.                               |
    |          |          | msgpack        |   1.1.0 | Encodes Python objects to MSGPack format.                                  |
    |          |          |                |         |                                                                            |
    |          | decode   | json           |   1.1.0 | Decodes JSON data to Python data objects.                                  |
    |          |          | msgpack        |   1.1.0 | Decodes MSGPack data into Python objects.                                  |
    |          |          |                |         |                                                                            |
    |          | function | header         |   1.1.0 | Adds information to event headers.                                         |
    |          |          | jsonvalidate   |   1.1.0 | Validates JSON data against JSON-schema.                                   |
    |          |          | keyvalue       |   1.1.0 | Adds the requested key values to the event data.                           |
    |          |          | loglevelfilter |   1.1.0 | Filters log events based on loglevel.                                      |
    |          |          | template       |   1.1.0 | A Wishbone module which generates a text from a dictionary and a template. |
    |          |          |                |         |                                                                            |
    |          | input    | amqp           |   1.1.0 | Consumes messages from AMQP.                                               |
    |          |          | dictgenerator  |   1.1.0 | Generates random dictionaries.                                             |
    |          |          | disk           |   1.1.0 | Reads messages from a disk buffer.                                         |
    |          |          | gearman        |   1.1.0 | Consumes events/jobs from  Gearmand.                                       |
    |          |          | httpclient     |   1.1.0 | A HTTP client doing http requests to pull data in.                         |
    |          |          | httpserver     |   1.1.0 | Receive events over HTTP.                                                  |
    |          |          | namedpipe      |   1.1.0 | Takes data in from a named pipe..                                          |
    |          |          | pull           |   1.1.0 | Pulls events from one or more ZeroMQ push modules.                         |
    |          |          | tcp            |   1.1.0 | A TCP server.                                                              |
    |          |          | testevent      |   1.1.0 | Generates a test event at the chosen interval.                             |
    |          |          | topic          |   1.1.0 | Subscribes to one or more ZeroMQ Topic publish modules.                    |
    |          |          | udp            |   1.1.0 | A UDP server.                                                              |
    |          |          |                |         |                                                                            |
    |          | output   | amqp           |   1.1.0 | Produces messages to AMQP.                                                 |
    |          |          | disk           |   1.1.0 | Writes messages to a disk buffer.                                          |
    |          |          | elasticsearch  |   1.1.0 | Submit data to Elasticsearch.                                              |
    |          |          | email          |   1.1.0 | Sends out incoming events as email.                                        |
    |          |          | file           |   1.1.0 | Writes events to a file                                                    |
    |          |          | http           |   1.1.0 | Posts data to the requested URL                                            |
    |          |          | null           |   1.1.0 | Purges incoming events.                                                    |
    |          |          | push           |   1.1.0 | Pushes events out to one or more ZeroMQ pull modules.                      |
    |          |          | sse            |   1.1.0 | A server sent events module.                                               |
    |          |          | stdout         |   1.1.0 | Prints incoming events to STDOUT.                                          |
    |          |          | syslog         |   1.1.0 | Writes log events to syslog.                                               |
    |          |          | tcp            |   1.1.0 | A TCP client which writes data to a TCP socket.                            |
    |          |          | topic          |   1.1.0 | Publishes data to one or more ZeroMQ Topic subscribe modules.              |
    |          |          | udp            |   1.1.0 | A UDP client which writes data to an UDP socket.                           |
    |          |          | uds            |   1.1.0 | Writes events to a Unix Domain Socket.                                     |
    |          |          |                |         |                                                                            |
    +----------+----------+----------------+---------+----------------------------------------------------------------------------+


------------------

**show**

Displays the docstring of the requested module.


.. code-block:: sh

    [smetj@indigo ~]$ wishbone show --module wishbone.flow.fanout
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 1.1.0

    Build event pipeline servers with minimal effort.


    ====================
    wishbone.flow.fanout
    ====================

    Version: 1.1.0

    Forward each incoming message to all connected queues.
    ------------------------------------------------------


        Forward each incoming message to all connected queues.

        Parameters:

            - deep_copy(bool)(True)
               |  make sure that each incoming event is submitted
               |  to the outgoing queues as a seperate event and not a
               |  reference.


        Queues:

            inbox
             |  Outgoing events.
