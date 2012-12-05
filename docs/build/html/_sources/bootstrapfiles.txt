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
              "metrics":true,
              "metrics_interval":10,
              "metrics_dst":"logging"
           },
           "bootstrap":{
              "broker":{
                 "module":"wishbone.io_modules.broker",
                 "class":"Broker",
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
                 "module":"wishbone.modules.brokerloopback",
                 "class":"BrokerLoopback",
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

**A bootstrap file consists out of 3 sections:**

system
------

This is an optional section.  It allows to you to configure the characteristics of the Wishbone setup.
Currently the available options here are:

Parameters:

- metrics (bool):               When true metrics are emitted every $metrics_interval seconds to $metrics_dst.
- metrics_interval (int):       The interval in seconds between dumping metrics. Default 10 seconds.
- metrics_dst (string):         Where to dump to metrics to. Default "logging". 

bootstrap
---------

The bootstrap section is where we define the Wishbone modules and their parameters to load and initialise.
The modules should be loadable from the Python search path, otherwise Wishbone will not be able to load them.

One section out consists out of following structure:

.. code-block:: text

    "The instance name when initiated.":{
                "module":"the name of the Python module to load",
                "class":"The name of the Python class to load",
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
