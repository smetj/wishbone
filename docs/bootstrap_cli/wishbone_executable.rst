===================
Wishbone executable
===================

The ``wishbone`` executable takes care of many aspects of setting up your service.
It accepts following commands:

* **start**

  .. code-block:: sh

      $ wishbone start --help
      usage: wishbone start [-h] [--config CONFIG] [--frequency FREQUENCY] [--graph]
                            [--graph_include_sys] [--identification IDENTIFICATION]
                            [--instances INSTANCES] [--log_level LOG_LEVEL] [--fork]
                            [--nocolor] [--pid PID] [--profile]
                            [--queue_size QUEUE_SIZE]

      Starts a Wishbone instance and detaches to the background. Logs are written to
      syslog.

      optional arguments:
        -h, --help            show this help message and exit
        --config CONFIG       The Wishbone bootstrap file to load.
        --frequency FREQUENCY
                              The metric frequency.
        --graph               When enabled starts a webserver on 8088 showing a
                              graph of connected modules and queues.
        --graph-include-sys   When enabled includes logs and metrics related queues
                              modules and queues to graph layout.
        --identification IDENTIFICATION
                              An identifier string for generated logs.
        --instances INSTANCES
                              The number of parallel Wishbone instances to
                              bootstrap.
        --loglevel  LOG_LEVEL
                              The maximum loglevel.
        --fork                When defined forks Wishbone to background and INFO
                              logs are written to STDOUT.
        --nocolor             When defined does not print colored output to stdout.
        --pid PID             The pidfile to use.
        --profile             When enabled profiles the process and dumps a Chrome
                              developer tools profile file in the current directory.
        --queue-size QUEUE_SIZE
                              The queue size to use.

* **list**

  .. code-block:: sh

      $ wishbone list --help
      usage: wishbone list [-h] [--namespace NAMESPACE]

      Lists the available modules.

      optional arguments:
        -h, --help            show this help message and exit
        --namespace NAMESPACE
                              The component namespace to query.

* **stop**

  .. code-block:: sh

      $ wishbone stop --help
      usage: wishbone stop [-h] [--pid PID]

      Tries to gracefully stop the Wishbone instance.

      optional arguments:
        -h, --help  show this help message and exit
        --pid PID   The pidfile to use.

* **show**

  .. code-block:: sh

      $ wishbone show --help
      usage: wishbone show [-h] (--docs DOCS | --code CODE)

      Shows information about a component.

      optional arguments:
        -h, --help   show this help message and exit
        --docs DOCS  Shows the documentation of the component.
        --code CODE  Shows the code of the refered component.
