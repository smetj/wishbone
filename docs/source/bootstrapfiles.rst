.. _bootstrapfiles:

==============
Bootstrapfiles
==============

Introduction
------------

Wishbone setups can be bootstrapped and started from command line using a bootstrapfile.
A bootstrap file allows you to configure the complete Wishbone setup without the need to dive into your Python code.
It's a practical way to deliver a fully configurable Wishbone based solution to your end users.

Example bootstrap file:

.. code-block:: text

        {
           "system":{
           },
           "metrics":{
              "enable":true,
              "group":"wishbone.metrics",
              "module":"Log",
              "interval":5,
              "variables":{
              }
           },
           "bootstrap":{
              "broker":{
                 "group":"wishbone.iomodule",
                 "module":"Broker",
                 "variables":{
                    "host":"localhost",
                    "vhost":"/",
                    "username":"guest",
                    "password":"guest",
                    "consume_queue":"wishbone",
                    "prefetch_count":100,
                    "no_ack":false
                 }
              },
              "loopback":{
                 "group":"wishbone.module",
                 "module":"BrokerLoopback",
                 "variables":{
                    "key":"wishbone",
                    "exchange":"",
                    "dump":500
                 }
              }
           },
           "routingtable":{
              "broker.inbox":[
                 "loopback.inbox"
              ],
              "loopback.outbox":[
                 "broker.outbox"
              ]
           }
        }

.. _bootstrapfiles_system:

**A bootstrap file consists out of 4 sections:**

system
------

This is an optional section.  It is reserverd for future use.

metrics
-------

The metrics section is obligatory.  It allows you to define a module which will handle the metrics.

Parameters:

- enable (bool):                When true, metrics are emitted.
- group (string):               Defines the entrypoint group in which the module is stored.
- module (string):              The name of the module (entrypoint).
- interval (int):               The interval in seconds between dumping metrics. Default 10 seconds.
- variables (dict):             Variables the module might require.

bootstrap
---------

The bootstrap section is where we define the Wishbone modules and their parameters to load and initialise.
The modules should be loadable from the Python search path, otherwise Wishbone will not be able to load them.

One section out consists out of following structure:

.. code-block:: text

    "The instance name when initiated.":{
                "group":"the name of the group containing the module. This is an entrypoint group.",
                "module":"The name of the Wishbone module to load. (Entrypoint)",
                "variables":{
                    "parameter1":x,
                    "parameter2":y,
                    "parameter3":z
                }
    }



routingtable
------------

The routing table determines which queues are connected to each other.

Currently we have 2 kinds of connections:

        - 1-1   : The most standard connection. Events from 1 queue go into another queue.
        - 1-n   : 1 to many connection.  This duplicates the events from 1 queue to each queue it is connected to.

The routing table has following format:

.. code-block:: text

    "routingtable":{
        "bootstrapInstanceName.queueName":[
            "bootstrapInstanceName.queueName"
        ],
        "bootstrapInstanceName.queueName":[
            "bootstrapInstanceName.queueName"
        ]
    }
