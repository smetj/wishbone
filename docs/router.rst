======
Router
======

The :py:class:`wishbone.router.Default` router is used to initialize the
modules and to organize the event stream between them.

Modules are registered using
:py:func:`wishbone.router.Default.registerModule`. The router takes care of
the proper startup :py:func:`wishbone.router.Default.start` and shutdown
:py:func:`wishbone.router.Default.stop` sequence of all the modules.

Queues are connected to each other using
:py:func:`wishbone.router.Default.connect`.  Queues can only have a "1 to 1"
relationship.  If you require a "1 to N" or similar scenario you might have to
use one of the builtin flow modules.

The router also takes care of the logs and metrics produced by the modules.
The :py:class:`wishbone.router.Default` router automatically connects the
*metrics* and *logs* queues of each module to a
:py:class:`wishbone.module.Funnel` module which can optionally be connected to
another module for further handling.


Logging
=======

Each module has an instance of :py:class:`wishbone.Logging`.  This class
offers the methods to generate logging with the appropriate level.

When modules are initialized in a router then the router it will automatically
connect the *logs* queue to a :py:class:`wishbone.module.Funnel` instance
called **logs_funnel**.  This module receives the logs from all modules. It is
up to the user to decide which other module(s) to connect to the *outbox* of
the *logs_funnel* to further process the logs.

Logs events are tuples have following format:

(6, 1367682301.430527, 'Router', 'Received SIGINT. Shutting down.')

Typically these log events are send to the :py:class:`wishbone.module.Syslog`.


Metrics
=======

Each modules proceses metrics of its queues.  Metrics are generated at the
defined <frequency>.

When modules are initialized in a router then the router it will automatically
connect the *metrics* queue to a :py:class:`wishbone.module.Funnel` instance
called **metrics_funnel**.  This module receives the metrics from all modules.
It is up to the user to decide which other module(s) to connect to the
*outbox* of the *metrics_funnel* to further process the metrics.

For each queue we have following metrics:

- dropped_rate
- dropped_total
- in_rate
- int_total
- out_rate
- out_total
- size


Typically a :py:class:`wishbone.module.Graphite` instance is connected to the
*metrics_funnel* module which in conjunction with
:py:class:`wishbone.module.TCPOut` sends the metrics to Graphite.

.. image:: graphite.png

Format
------
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

        (1381002603.726132, 'wishbone', 'hostname', 'queue.outbox.in_rate', 0, '', ("production",monitored))