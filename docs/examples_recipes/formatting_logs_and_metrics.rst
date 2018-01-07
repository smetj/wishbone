=========================
Handling logs and metrics
=========================

When bootstrapping an instance using the ``wishbone`` executable and
:py:class:`wishbone.config.configfile.ConfigFile` is used to generate a
``router`` configuration.

Review the :py:class:`wishbone.config.configfile.ConfigFile` docstring to read
about the parts which are confiured automatically.


Shipping metrics
----------------

Wishbone metric events are just plain Wishbone events.

.. code-block:: javascript

    {'cloned': False, 'bulk': False, 'data': {'time': 1511013563.2159407, 'type': 'wishbone', 'source': 'indigo', 'name': 'module.input.queue._metrics.size', 'value': 0, 'unit': '', 'tags': ()}, 'errors': {}, 'tags': [], 'timestamp': 1511013563.2159421, 'tmp': {}, 'ttl': 252, 'uuid_previous': [], 'uuid': '76b331e8-d088-4002-b772-0df613c6f757'}
    {'cloned': False, 'bulk': False, 'data': {'time': 1511013563.2159586, 'type': 'wishbone', 'source': 'indigo', 'name': 'module.input.queue._metrics.in_total', 'value': 35, 'unit': '', 'tags': ()}, 'errors': {}, 'tags': [], 'timestamp': 1511013563.2159598, 'tmp': {}, 'ttl': 252, 'uuid_previous': [], 'uuid': 'ccabd8ac-420f-4e6d-a89a-b53351e887e1'}
    {'cloned': False, 'bulk': False, 'data': {'time': 1511013563.215973, 'type': 'wishbone', 'source': 'indigo', 'name': 'module.input.queue._metrics.out_total', 'value': 35, 'unit': '', 'tags': ()}, 'errors': {}, 'tags': [], 'timestamp': 1511013563.215974, 'tmp': {}, 'ttl': 252, 'uuid_previous': [], 'uuid': '16717619-c525-4e33-9f7d-35bdf42819be'}
    {'cloned': False, 'bulk': False, 'data': {'time': 1511013563.2160392, 'type': 'wishbone', 'source': 'indigo', 'name': 'module.input.queue._metrics.in_rate', 'value': 3.4852626619479707, 'unit': '', 'tags': ()}, 'errors': {}, 'tags': [], 'timestamp': 1511013563.2160406, 'tmp': {}, 'ttl': 252, 'uuid_previous': [], 'uuid': '2d80683d-100b-45d9-b8a5-68cff227bbae'}
    {'cloned': False, 'bulk': False, 'data': {'time': 1511013563.216054, 'type': 'wishbone', 'source': 'indigo', 'name': 'module.input.queue._metrics.out_rate', 'value': 3.485262248221764, 'unit': '', 'tags': ()}, 'errors': {}, 'tags': [], 'timestamp': 1511013563.2160554, 'tmp': {}, 'ttl': 252, 'uuid_previous': [], 'uuid': 'c3e3c916-4b6d-4df4-845a-f2f71097d339'}
    {'cloned': False, 'bulk': False, 'data': {'time': 1511013563.2160676, 'type': 'wishbone', 'source': 'indigo', 'name': 'module.input.queue._metrics.dropped_total', 'value': 0, 'unit': '', 'tags': ()}, 'errors': {}, 'tags': [], 'timestamp': 1511013563.216069, 'tmp': {}, 'ttl': 252, 'uuid_previous': [], 'uuid': '69cf9aeb-32ef-4b61-80e2-f45cdfe0ccb5'}


If we want to send Wishbone internal metrics to Graphite we use
:py:class:`wishbone.module.process.template <wishbone.module.template.Template>`
module in order to convert the above JSON into the desired Graphite format.

.. NOTE::
   The ``wishbone.module.output.tcp`` is an external module which has to be
   installed separately

.. code-block:: yaml

    modules:
      input:
        module: wishbone.module.input.generator
        arguments:
          payload: hello world

      output:
        module: wishbone.module.output.stdout

      metrics_graphite:
        module: wishbone.module.process.template
        arguments:
          templates:
            graphite: 'wishbone.{{data.name}} {{data.value}} {{data.time}}'

      metrics_pack:
        module: wishbone.module.process.pack
        arguments:
          bucket_size: 1500


      metrics_out:
        module: wishbone_external.module.output.tcp
        arguments:
          selection: graphite
          host: graphite-host.some.domain
          port: 2013

    routingtable:
      - input.outbox -> output.inbox

      - _metrics.outbox         -> metrics_graphite.inbox
      - metrics_graphite.outbox -> metrics_pack.inbox
      - metrics_pack.outbox     -> metrics_out.inbox


- The ``metrics_graphite`` module instance `assembles` the fields of the
  events containing the metrics into a format Graphite understands.

- The ``wishbone_external.module.output.tcp`` opens and closes a connection
  per event.  This is not very efficient hence we put a
  :py:class:`wishbone.module.process.pack <wishbone.module.pack.Pack>` module
  in front of the output in order to submit buckets of 1500 metrics per
  connection.


Shipping logs
-------------

Instead of sending formatted logs to STDOUT or SYSLOG you might want to ship
the Wishbone log events in JSON format to STDOUT.

You could do that using following bootstrap file:

.. code-block:: yaml

    protocols:
      json:
        protocol: wishbone.protocol.encode.json

    modules:
      input:
        module: wishbone.module.input.generator
        arguments:
          payload: hello world

      output:
        module: wishbone.module.output.stdout

      logs_out:
        protocol: json
        module: wishbone.module.output.stdout
        arguments:
          selection: data

    routingtable:
      - input.outbox -> output.inbox

      - _logs.outbox -> logs_out.inbox


Starting the Wishbone instance in foreground would give following result:

.. code-block:: sh

    $ wishbone start --config hello_world_logs.yaml
    Instance started in foreground with pid 11126
    {"time": 1511022472.4646914, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Connected queue _logs._logs to _logs.__logs"}
    {"time": 1511022472.4647346, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Connected queue _logs._metrics to _metrics.__logs"}
    {"time": 1511022472.4647586, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Module instance '_logs' has no queue '__logs_filter' so auto created."}
    {"time": 1511022472.464825, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Module instance '_logs' has no queue '__metrics' so auto created."}
    {"time": 1511022472.4648945, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Module instance '_logs' has no queue '_input' so auto created."}
    {"time": 1511022472.464962, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Module instance '_logs' has no queue '_output' so auto created."}
    {"time": 1511022472.4650266, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Module instance '_logs' has no queue '_logs_out' so auto created."}
    {"time": 1511022472.4651015, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Connected queue _logs.outbox to logs_out.inbox"}
    {"time": 1511022472.465119, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Following template functions are available: strftime, epoch, version"}
    {"time": 1511022472.4651282, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "preHook() found, executing"}
    {"time": 1511022472.4651651, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Started with max queue size of 100 events and metrics interval of 10 seconds."}
    {"time": 1511022472.4688632, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs", "message": "Function 'consume' has been registered to consume queue '__logs'"}
    {"time": 1511022472.46477, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs_filter", "message": "Connected queue _logs_filter._logs to _logs.__logs_filter"}
    {"time": 1511022472.464803, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs_filter", "message": "Connected queue _logs_filter._metrics to _metrics.__logs_filter"}
    {"time": 1511022472.4651802, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs_filter", "message": "Following template functions are available: strftime, epoch, version"}
    {"time": 1511022472.4651895, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs_filter", "message": "preHook() found, executing"}
    {"time": 1511022472.4652004, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs_filter", "message": "Module has no preHook() method set."}
    {"time": 1511022472.4652123, "identification": "wishbone", "event_id": null, "level": 7, "txt_level": "debug", "pid": 11126, "module": "_logs_filter", "message": "Started with max queue size of 100 events and metrics interval of 10 seconds."}


