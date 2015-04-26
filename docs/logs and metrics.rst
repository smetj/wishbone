================
Logs and metrics
================

Logging
-------

Each module has an instance of :py:class:`wishbone.Logging` offering a
function for each loglevel.

When modules are initialized by the router, it will automatically connect the
*logs* queue of all modules to a :py:class:`wishbone.module.Funnel` instance
called **wishbone_logs**. This module receives the logs from all modules. It
is up to the user to decide which other module(s) to connect to the *outbox*
of the *wishbone_logs* to further process the logs.

Logs events are tuples have following format:

(6, 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')

Typically these log events are send to the :py:class:`wishbone.module.Syslog`
or to :py:class:`wishbone.encode.HumanLogFormat` and
:py:class:`wishbone.module.STDOUT`.


Metrics
-------

Each modules collects and produces metrics of all its queues.  Metrics are
generated at the defined <frequency> (see cli options).

When modules are initialized by the router, it will automatically connect the
*metrics* queue al all modules to a :py:class:`wishbone.module.Funnel`
instance called **wishbone_metrics**. This module receives the metrics from
all modules. It is up to the user to decide which other module(s) to connect
to the *outbox* of the *wishbone_metrics* to further process the logs.

For each queue we have following metrics:

- dropped_rate
- dropped_total
- in_rate
- int_total
- out_rate
- out_total
- size


Typically a :py:class:`wishbone.module.Graphite` instance is connected to the
*wishbone_metrics* module instance which in conjunction with
:py:class:`wishbone.module.TCPOut` sends the metrics to Graphite.

.. image:: graphite.png


Format
~~~~~~

Wishbone represents metrics into a fixed data structure:

    (time, type, source, name, value, unit, (tag1, tag2))

It is a tuple containing a number of fields:

- timestamp
  A timestamp of the metric in unix time.

- type
  A free to choose description of the type of the metric

- source
  The originating source of the metric

- name
  The name of the metric

- value
  The metric value

- unit
  The value units

- tags
  A tuple of tags

For example:

.. code-block:: python

        (1381002603.726132, 'wishbone', 'hostname', 'queue.outbox.in_rate', 0, '', ("production",monitored))