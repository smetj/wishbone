.. _bootstrapfiles:

==============
Bootstrapfiles
==============

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
- system
  - metrics
  - metrics_interval
  - metrics_dst


