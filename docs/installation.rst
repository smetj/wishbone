============
Installation
============


Wishbone
--------

Pypi
'''''

You can install the latest stable version of Wishbone from
https://pypi.python.org/pypi/wishbone/ by using pip:

.. code-block:: sh

    $ pip install wishbone

All dependencies should be resolved automatically.


From source
'''''''''''

You can install the latest stable or development version from
https://github.com/smetj/wishbone

Stable
~~~~~~

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone
    $ cd wishbone
    $ cd checkout master #just in case your repo is in another branch
    $ sudo python setup.py install


Development
~~~~~~~~~~~

To install the latest development release you have to checkout the develop
branch and build from there:

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone.git
    $ cd wishbone
    $ git checkout develop
    $ sudo python setup.py install


Docker
''''''

As of version 0.5 a Docker container of Wishbone is available.
TODO(smetj): more info


Verify installation
'''''''''''''''''''
x
Once installed you should have the `wishbone` executable available in your search
path:

.. code-block:: sh

    $ wishbone --help
    usage: wishbone [-h] {start,debug,stop,kill,list,show} ...

    Wishbone bootstrap server.

    positional arguments:
      {start,debug,stop,kill,list,show}

    optional arguments:
      -h, --help            show this help message and exit


Modules
-------

Builtin modules
'''''''''''''''

Wishbone comes with a set of builtin modules.  You can verify the available
default modules by using the *list* command:

.. code-block:: sh

    $ wishbone list
    +----------+----------+------------+---------+------------------------------------------------------------+
    | Category | Group    | Module     | Version | Description                                                |
    +----------+----------+------------+---------+------------------------------------------------------------+
    |          |          |            |         |                                                            |
    | wishbone | flow     | funnel     |   0.5.0 | Funnel multiple incoming queues to 1 outgoing queue.       |
    |          |          | fanout     |   0.5.0 | Funnel multiple incoming queues to 1 outgoing queue.       |
    |          |          | roundrobin |   0.5.0 | Round-robins incoming events to all connected queues.      |
    |          |          |            |         |                                                            |
    |          | function | header     |   0.5.0 | Adds information to event headers.                         |
    |          |          |            |         |                                                            |
    |          | input    | disk       |   0.5.0 | Reads messages from a disk buffer.                         |
    |          |          | testevent  |   0.5.0 | Generates a test event at the chosen interval.             |
    |          |          | tcp        |   0.5.0 | A Wishbone input module which listens on a TCP socket.     |
    |          |          | amqp       |   0.5.0 | Consumes messages from AMQP.                               |
    |          |          |            |         |                                                            |
    |          | output   | disk       |   0.5.0 | Writes messages to a disk buffer.                          |
    |          |          | amqp       |   0.5.0 | Produces messages to AMQP.                                 |
    |          |          | stdout     |   0.5.0 | Prints incoming events to STDOUT.                          |
    |          |          | tcp        |   0.5.0 | A Wishbone ouput module which writes data to a TCP socket. |
    |          |          | syslog     |   0.5.0 | Writes log events to syslog.                               |
    |          |          | null       |   0.5.0 | Purges incoming events.                                    |
    |          |          |            |         |                                                            |
    +----------+----------+------------+---------+------------------------------------------------------------+


Modules are stored into a hierarchic name space.  The complete name of a
module consists out of the category name + group name + module name.  You can read the details of a module by executing the *show* command:

.. code-block:: sh

    $ wishbone show --module wishbone.input.testevent
    Module "wishbone.input.testevent" version 0.5.0
    ===============================================

    Generates a test event at the chosen interval.
    ----------------------------------------------



        Events have following format:

            { "header":{}, "data":"test" }

        Parameters:

            -   name(str)
                The name of the module.

            -   size(int)
                The default max length of each queue.

            -   frequency(int)
                The frequency in seconds to generate metrics.

            - interval (float):     The interval in seconds between each generated event.
                                    A value of 0 means as fast as possible.
                                    default: 1

            - message (string):     The content of the test message.
                                    default: "test"

            - numbered (bool):      When true, appends a sequential number to the end.
                                    default: False

        Queues:

            - outbox:    Contains the generated events.

    $



External modules
''''''''''''''''

Not all modules are builtin modules.  There is a collection of modules which
can be downloaded from https://github.com/smetj/wishboneModules. Any Wishbone
modules which are not an inherent part of the project itself will be installed
in the *wishbone.contrib* category.

Installing a "contrib" module typically involves installing the provided
packages through **pypi** or by installing the Python package manually.

.. code-block:: sh

    $ git clone https://github.com/smetj/wishboneModules.git
    $ cd wb_output_tcp
    $ python setup.py install
    $ wishbone show wishbone.output.tcp
    **A Wishbone IO module which writes data to a TCP socket.**

    Writes data to a tcp socket.

    Parameters:

        - name (str):       The instance name when initiated.

        - host (string):    The host to submit to.
                            Default: "localhost"

        - port (int):       The port to submit to.
                            Default: 19283

        - timeout(int):     The time in seconds to timeout when
                            connecting
                            Default: 1

        - delimiter(str):   A delimiter to add to each event.
                            Default: "\n"

        - success (bool):   When True, submits succesfully outgoing
                            events to the 'success' queue.
                            Default: False

        - failed (bool):    When True, submits failed outgoing
                            events to the 'failed' queue.
                            Default: False

    Queues:

        - inbox:    Incoming events submitted to the outside.

        - success:  Contains events which went out succesfully.
                    (optional)

        - failed:   Contains events which did not go out successfully.
                    (optional)