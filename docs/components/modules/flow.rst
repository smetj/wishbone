====
Flow
====
.. _flow:

.. note::

    Flow modules apply logic of some sort to decide which queue to submit the
    event to without altering the event's payload.

Flow modules select the outgoing queue to which incoming events are submitted
based on certain conditions.  For example, Wishbone queues can only be
connected 1 queue.

If you need a `1-to-many` or a `many-to-1` queue connection then you can use
the :py:class:`wishbone.module.fanout.Fanout` or
:py:class:`wishbone.module.funnel.Funnel` respectively.

Some of the characteristics of `flow` modules are:

* They do not alter the content of events flowing through except optionally
  setting some contextual data.

The builtin flow modules are:

+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| Name                                                                                    | Description                                                             |
+=========================================================================================+=========================================================================+
| :py:class:`wishbone.module.flow.acknowledge <wishbone.module.acknowledge.Acknowledge>`  | Forwards or drops events by acknowleding values.                        |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| :py:class:`wishbone.module.flow.count <wishbone.module.count.Count>`                    | Pass or drop events based on the number of times an event value occurs. |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| :py:class:`wishbone.module.flow.fanout <wishbone.module.fanout.Fanout>`                 | Forward each incoming message to all connected queues.                  |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| :py:class:`wishbone.module.fresh.Fresh <wishbone.module.fresh.Fresh>`                   | Generates a new event unless an event came through in the last x time.  |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| :py:class:`wishbone.module.funnel.Funnel <wishbone.module.funnel.Funnel>`               | Funnel multiple incoming queues to 1 outgoing queue.                    |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| :py:class:`wishbone.module.flow.queueselect <wishbone.module.queueselect.QueueSelect>`  | Submits message to the queue defined by a rendered template.            |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| :py:class:`wishbone.module.flow.roundrobin <wishbone.module.roundrobin.RoundRobin>`     | Round-robins incoming events to all connected queues.                   |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+
| :py:class:`wishbone.module.flow.switch <wishbone.module.switch.Switch>`                 | Switch outgoing queues while forwarding events.                         |
+-----------------------------------------------------------------------------------------+-------------------------------------------------------------------------+

