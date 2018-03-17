======
Output
======
.. _output:

.. note::

    Output modules submit data to external services.


 `Output` module properties:

* They have a :ref:`protocol encoder method <encode>` mapped to
  :func:`wishbone.module.OutputModule.encode` in order to convert the desired
  :py:class:`wishbone.event.Event` payload into the desired format prior to
  submitting it to the external service.

* Should **always** provide a ``selection``, ``payload``, ``native_events``
  and ``parallel_streams`` module parameter. If ``payload`` is not ``None``,
  then it takes precendence over ``selection``. ``Selection`` defines the
  event key to submit whilst template comes up with a string to
  submit.``payload`` usually makes no sense with bulk events.

* Should use :func:`wishbone.module.OutputModule.getDataToSubmit` to retrieve
  the actual data to submit to the external service.This automatically takes
  care of :ref:`bulk events <bulk_events>`.

* Through inheriting :py:class:`wishbone.module.OutputModule` `Output` modules
  override :func:`wishbone.actor.Actor._consumer` with their own version which
  executes the registered ``function`` in parallel greenthreads by using a
  threadpool. The module's ``parallel_streams`` parameter defines the size of
  the pool and therefor the number of parallel greenthreads submitting the
  event data externally.It depends on the nature of your output protocol
  whether this makes sense.Normally you shouldn't really bother with this as
  long a Gevent's monkey patching works on the code you're using to speak to
  the remote service.


.. WARNING::

    Be aware that if ``parallel_streams`` is larger than 1, the equal amount
    of events will be processed concurrently by the function registered with
    :func:`wishbone.actor.Actor.registerConsumer` to consume the queue. Within
    that function do **NOT** change shared (module) variables but only use
    local (to the function) ones.


The builtin Wishbone Output modules:

+-----------------------------------------------------------------------------+-----------------------------------+
| Name                                                                        | Description                       |
+=============================================================================+===================================+
| :py:class:`wishbone.module.output.null <wishbone.module.null.Null>`         | Purges events.                    |
+-----------------------------------------------------------------------------+-----------------------------------+
| :py:class:`wishbone.module.output.stdout <wishbone.module.stdout.STDOUT>`   | Prints event data to STDOUT.      |
+-----------------------------------------------------------------------------+-----------------------------------+
| :py:class:`wishbone.module.output.syslog <wishbone.module.wbsyslog.Syslog>` | Submits event data to syslog.     |
+-----------------------------------------------------------------------------+-----------------------------------+


-----

``Output`` modules must base :py:class:`wishbone.module.OutputModule`:


.. autoclass:: wishbone.module.OutputModule
    :members:
    :show-inheritance:
    :inherited-members:
