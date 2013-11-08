============
Installation
============


Wishbone
--------

Pypi
'''''

You can install the latest stable version of Wishbone from
https://pypi.python.org/pypi/wishbone/ by using easy_install or pip:



.. code-block:: sh

    $ easy_install wishbone

Or

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


Verify installation
'''''''''''''''''''

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
    Available Wishbone modules:
    +---------------------------+-------------------+---------+----------------------------------------------------------------------+
    | Group                     | Module            | Version | Description                                                          |
    +---------------------------+-------------------+---------+----------------------------------------------------------------------+
    | wishbone.builtin.logging  | loglevelfilter    | 0.4.8   | Filters Wishbone log events.                                         |
    |                           | humanlogformatter | 0.4.8   | Formats Wishbone log events.                                         |
    |                           |                   |         |                                                                      |
    | wishbone.builtin.metrics  | graphite          | 0.4.8   | Converts the internal metric format to Graphite format.              |
    |                           |                   |         |                                                                      |
    | wishbone.builtin.flow     | roundrobin        | 0.4.8   | Round-robins incoming events to all connected queues.                |
    |                           | fanout            | 0.4.8   | Duplicates incoming events to all connected queues.                  |
    |                           | tippingbucket     | 0.4.8   | Event buffer module.                                                 |
    |                           | funnel            | 0.4.8   | Merges incoming events from multiple queues to 1 queue.              |
    |                           | lockbuffer        | 0.4.8   | A module with a fixed size inbox queue.                              |
    |                           |                   |         |                                                                      |
    | wishbone.builtin.function | header            | 0.4.8   | Adds information to event headers.                                   |
    |                           |                   |         |                                                                      |
    | wishbone.builtin.input    | testevent         | 0.4.8   | Generates a test event at the chosen interval.                       |
    |                           |                   |         |                                                                      |
    | wishbone.builtin.output   | syslog            | 0.4.8   | Writes log events to syslog.                                         |
    |                           | null              | 0.4.8   | Purges incoming events..                                             |
    |                           | stdout            | 0.4.8   | Prints incoming events to STDOUT.                                    |
    |                           | slow              | 0.4.8   | Processes an incoming event per X seconds.                           |
    |                           |                   |         |                                                                      |
    +---------------------------+-------------------+---------+----------------------------------------------------------------------+

Modules are stored into a hierarchic name space.  The complete name of a
module consists out of the group name + the module name.  You can read the details of a module by executing the *show* command:

.. code-block:: sh

    $ wishbone show wishbone.builtin.input.testevent
    **Generates a test event at the chosen interval.**

        This module is only available for testing purposes and has further hardly any use.

        Events have following format:

            { "header":{}, "data":"test" }

        Parameters:

            - name (str):               The instance name when initiated.

            - interval (float):         The interval in seconds between each generated event.
                                        Should have a value > 0.
                                        default: 1

        Queues:

            - outbox:    Contains the generated events.


External modules
''''''''''''''''

Not all modules are builtin modules.  There is a collection of modules which
can be downloaded from https://github.com/smetj/wishboneModules.  The reason
they are not builtin modules is to limit the number of dependencies for
Wishbone itself.  All modules are also in 1 repository.  Within time they will
be available as separate projects and added to Pypi.

To install an *external* module follow these steps:

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