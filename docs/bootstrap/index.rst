=========
Bootstrap
=========

    *Boostrapping a Wishbone server on CLI is done using a YAML config file
    which describes the modules to initialize and their connections.*


Example:

.. code:: sh

    $ wishbone start --config /etc/wishbone_bootstrap.yaml --pid /var/run/wishbone.pid

.. toctree::
    commands/index
    bootstrap_files/index

Logs
----

The bootstrap process  is responsible for loading and initializing the
event modules automatically connects the ``logs`` queue of each module to
a :py:class:`wishbone.module.funnel.Funnel` instance named ``_logs``.  This
module then effectively receives all log events.

If the user decides not to connect the ``_logs.outbox`` queue to another
module then the bootstrap process will automatically initialize additional
modules to send these to either SYSLOG or STDOUT depending on it's started to
run in the background (--start) or foreground (--debug) respectively.

If you would like to forward the log events of all the modules to a module of
your choice, you can achieve this by connecting the ``_logs.outbox`` queue to
the desired module.

Metrics
-------

The bootstrap process  is responsible for loading and initializing the
event modules automatically connects the ``metrics`` queue of each module to
a :py:class:`wishbone.module.funnel.Funnel` instance named ``_metrics``.  This
module then effectively receives all metric events.

If the user decides not to connect the ``_metrics.outbox`` queue to another
module all metrics will simply be dropped.


By default the ``_metrics.outbox`` queue is not connected to another module
(in contrary to ``_logs.outbox``) therefor all metric data is lost by default.
If however you would like to process the Wishbone metrics externally you can
hook up the necessary modules to **_metrics.outbox** to achieve the desired
result.

.. note::

    The ``--frequency`` parameter determines the rate metrics are collected.


For example you can forward the Wishbone metrics to Graphite by chaining
`wishbone.encode.graphite`_ (converts :py:class:`wishbone.event.Metric` into a
Graphite format) and `wishbone.output.tcp`_ (submits the Graphite data over TCP
to Graphite).

.. image:: ../../_images/graphite.png
.. _wishbone.encode.graphite: https://pypi.org/project/wishbone_encode_graphite
.. _wishbone.output.tcp: https://pypi.org/project/wishbone_output_tcp/



