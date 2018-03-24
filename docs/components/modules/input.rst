=====
Input
=====
.. _input:

.. note::

    Input modules either take events from the outside world or generate events.


**Input module properties**:


* They have a :ref:`protocol decoder method <decode>` mapped to
  :func:`wishbone.module.InputModule.decode` in order to convert the incoming
  data into a workable datastructure.

* :paramref:`wishbone.actorconfig.ActorConfig.protocol_function` determines
  whether :func:`wishbone.module.InputModule.generateEvent` either expects
  events from the outside world to be Wishbone events or regular data.

* Contextual data about the incoming event can/should be stored under
  ``tmp.<module name>``.

* Should always have an ``destination`` and ``native_events`` parameter.

* Should use :func:`wishbone.actor.Actor.generateEvent` to generate the event
  in which to store the incoming data.  It takes care of how the event is created
  in relation to the obligatory ``destination`` and ``native_events`` parameters.

* If you're setting a default decoder function make sure you use
  :func:`wishbone.module.InputModule.setDecoder` as this method will prevent
  overwrite any user defined decoder set via
  :py:class:`wishbone.actorconfig.ActorConfig`.


The builtin Wishbone Input modules:

+-----------------------------------------------------------------------------------+------------------------------------------------+
| Name                                                                              | Description                                    |
+===================================================================================+================================================+
| :py:class:`wishbone.module.input.cron <wishbone.module.cron.Cron>`                | Generates an event at the defined time.        |
+-----------------------------------------------------------------------------------+------------------------------------------------+
| :py:class:`wishbone.module.input.generator <wishbone.module.generator.Generator>` | Generates an event at the chosen interval.     |
+-----------------------------------------------------------------------------------+------------------------------------------------+
| :py:class:`wishbone.module.input.inotify <wishbone.module.wb_inotify.WBInotify>`  | Monitors one or more paths for inotify events. |
+-----------------------------------------------------------------------------------+------------------------------------------------+


-----

``Input`` modules must base :py:class:`wishbone.module.InputModule`:

.. autoclass:: wishbone.module.InputModule
    :members:
    :show-inheritance:
    :inherited-members:
