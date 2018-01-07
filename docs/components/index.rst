==========
Components
==========
.. _complete:

A Wishbone service consists out of a combination of different components.
Wishbone has 3 component types:

.. toctree::
    :maxdepth: 1

    modules/index
    functions/index
    protocols/index


Components are referred to with a unique name written in dotted format:


.. code-block:: text

    <namespace>.<component type>.<category>.<name>


``namespace`` is a logical grouping for components.  The ``wishbone``
namespace indicates the component is an one part of the default Wishbone
installation or the Wishbone project.  If you develop additional components
outside of the Wishbone project itself, it is advised to do so in its
dedicated namespace.

``component type``, ``category`` and ``name`` further categorize the the components into logical groupings.

Each component has an `entrypoint`_ so it can be referred to from a bootstrap
file or referred to using
:py:func:`wishbone.componentmanager.ComponentManager.getComponentByName`. The
default Wishbone entrypoints are defined in its setup.py file. A component
entrypoint is the same as the component name.


An overview of available components can be viewed by using the ``list`` command:

.. tip::

    By default, the Wishbone executable includes the ``wishbone_contrib`` and
    ``wishbone_external`` into its searchpath when searching for available
    modules.


.. code-block:: text

    $ wishbone list
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 3.0.0

    Build composable event pipeline servers with minimal effort.


    Available components:
    +-----------+----------------+----------+----------------+---------+-------------------------------------------------------------------------+
    | Namespace | Component type | Category | Name           | Version | Description                                                             |
    +-----------+----------------+----------+----------------+---------+-------------------------------------------------------------------------+
    |           |                |          |                |         |                                                                         |
    | wishbone  | protocol       | decode   | dummy          |   3.0.0 | A dummy decoder.                                                        |
    |           |                |          | json           |   3.0.0 | Decode JSON data into a Python data structure.                          |
    |           |                |          | msgpack        |   3.0.0 | Decode MSGpack data into a Python data structure.                       |
    |           |                |          | plain          |   3.0.0 | Decode text data into a Python data structure.                          |
    |           |                |          |                |         |                                                                         |
    |           |                | encode   | dummy          |   3.0.0 | A dummy encoder.                                                        |
    |           |                |          | json           |   3.0.0 | Encode data into JSON format.                                           |
    |           |                |          | msgpack        |   3.0.0 | Encode data into msgpack format.                                        |
    |           |                |          |                |         |                                                                         |
    |           | function       | module   | append         |   3.0.0 | Adds <data> to the array <destination>.                                 |
    |           |                |          | lowercase      |   3.0.0 | Puts the desired field in lowercase.                                    |
    |           |                |          | set            |   3.0.0 | Sets a field to the desired value.                                      |
    |           |                |          | uppercase      |   3.0.0 | Puts the desired field in uppercase.                                    |
    |           |                |          |                |         |                                                                         |
    |           |                | template | choice         |   3.0.0 | Returns a random element from the provided array.                       |
    |           |                |          | cycle          |   3.0.0 | Cycles through the provided array returning the next element.           |
    |           |                |          | epoch          |   3.0.0 | Returns epoch with sub second accuracy as a float.                      |
    |           |                |          | pid            |   3.0.0 | Returns the PID of the current process.                                 |
    |           |                |          | random_bool    |   3.0.0 | Randomly returns True or False                                          |
    |           |                |          | random_integer |   3.0.0 | Returns a random integer.                                               |
    |           |                |          | random_uuid    |   3.0.0 | Returns a uuid value.                                                   |
    |           |                |          | random_word    |   3.0.0 | Returns a random word.                                                  |
    |           |                |          | regex          |   3.0.0 | Regex matching on a string.                                             |
    |           |                |          | strftime       |   3.0.0 | Returns a formatted version of an epoch timestamp.                      |
    |           |                |          |                |         |                                                                         |
    |           | module         | flow     | acknowledge    |   3.0.0 | Forwards or drops events by acknowleding values.                        |
    |           |                |          | count          |   3.0.0 | Pass or drop events based on the number of times an event value occurs. |
    |           |                |          | fanout         |   3.0.0 | Forward each incoming message to all connected queues.                  |
    |           |                |          | fresh          |   3.0.0 | Generates a new event unless an event came through in the last x time.  |
    |           |                |          | funnel         |   3.0.0 | Funnel multiple incoming queues to 1 outgoing queue.                    |
    |           |                |          | queueselect    |   3.0.0 | Submits message to the queue defined by a rendered template.            |
    |           |                |          | roundrobin     |   3.0.0 | Round-robins incoming events to all connected queues.                   |
    |           |                |          | switch         |   3.0.0 | Switch outgoing queues while forwarding events.                         |
    |           |                |          |                |         |                                                                         |
    |           |                | input    | cron           |   3.0.0 | Generates an event at the defined time                                  |
    |           |                |          | generator      |   3.0.0 | Generates an event at the chosen interval.                              |
    |           |                |          | inotify        |   3.0.0 | Monitors one or more paths for inotify events.                          |
    |           |                |          |                |         |                                                                         |
    |           |                | output   | null           |   3.0.0 | Purges incoming events.                                                 |
    |           |                |          | stdout         |   3.0.0 | Prints incoming events to STDOUT.                                       |
    |           |                |          | syslog         |   3.0.0 | Writes log events to syslog.                                            |
    |           |                |          |                |         |                                                                         |
    |           |                | process  | modify         |   3.0.0 | Modify and manipulate datastructures.                                   |
    |           |                |          | pack           |   3.0.0 | Packs multiple events into a bulk event.                                |
    |           |                |          | template       |   3.0.0 | Renders Jinja2 templates.                                               |
    |           |                |          | unpack         |   3.0.0 | Unpacks bulk events into single events.                                 |
    |           |                |          |                |         |                                                                         |
    +-----------+----------------+----------+----------------+---------+-------------------------------------------------------------------------+


.. _entrypoint: https://docs.pylonsproject.org/projects/pylons-webframework/en/latest/advanced_pylons/entry_points_and_plugins.html
