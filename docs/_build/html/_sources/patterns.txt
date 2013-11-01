============================
Patterns and best practices
============================

This section discusses some common usage patterns and best practices. Although
most if not all are strictly spoken not required, they might be helpful in
building efficient Wishbone solutions.

Event headers
-------------

Write data to headers
~~~~~~~~~~~~~~~~~~~~~

In its bare minimum, an event has following layout:

.. code-block:: python

    { "header":{}, "data": object }

Whenever a module writes data into the header section of the event, it should
store this under the <self.name> key, which is unique anyway within a router
instance.

The <self.name> value of a module is determined when registering the module
using :py:func:`wishbone.router.Default.register`.

So when registering a module like this:

.. code-block:: python

    router = Default(interval=1)
    router.register(STDOUT, "on_screen")

Then any information this module instance wants to write into the header
should look like:

.. code-block:: python

    { "header":{"on_screen":{"one":1, "two":2}}, "data": object }


Retrieving data from headers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a module requires specific information from the header which has been
stored by another it should be possible to initiate the module using a
parameter named "key".  You should not hard code the name of the header key
into the module because if someone registers a module with another name, your
code will not work anymore.

Consider following example module:

.. code-block:: python

    class Output(Actor):
        def __init__(self, name, key=None):
            Actor.__init__(self, name)
            self.name=name
            if key == None:
                self.key=self.name
            else:
                self.key=key

        def consume(self, event):
            print event["header"][self.key]["one"]


Writing output modules
----------------------

Starting state
~~~~~~~~~~~~~~

An output module should always start with the **inbox** queue in a
:py:func:`wishbone.tools.WishboneQueue.putLock` state.  The moment the module
detects it is capable of sending incoming events to the outside world, it
should unlock the **inbox** queue using
:py:func:`wishbone.tools.WishboneQueue.putUnlock`.

Handle failed and successful events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output modules are responsible to deliver messages to the outside world.
Preferably we want this to be done as reliably.  When submitting events to the
outside world (aka outside a Wishbone process.) fails or succeeds we might
require a specific strategy to deal with that specific situation.

A possible strategy is have 2 additional queues:

    - successful
    - failed

As you might guess, events which have been submitted successfully to the
outside world are then submitted to the *successful* queue while the events
which failed to go out to the *failed* queue.

It is up the user to connect these queues on their turn to another destination
in order come to the desired strategy.

Some practical examples:

- After submitting an event successfully over TCP to the outside world is is
  submitted to the `successful` queue.  This queue is on its turn connected to
  the AMQP `acknowledge` queue to ascertain it is acknowledged from AMQP.

- After submitting an event over TCP failed, the event is written to the
  failed queue from where it is forwarded to another module which writes the
  event to disk.

Whenever this pattern is *not* used, the expected behavior should be:

- Successfully submitted events are discarded
- Unsuccessfully submitted events should be send back to the `inbox` queue
  using :py:func:`wishbone.tools.WishboneQueue.rescue`.



Retrying and monitors
~~~~~~~~~~~~~~~~~~~~~

When possible an output module should have a "monitor" thread running
endlessly in a separate greenthread trying to create a valid connection object
to the outside service.

This monitor process should be blocked until :py:func:`wishbone.Actor.consume`
fails to submit an event via the connection object.

During the time the monitor process is retrying to create a valid connection
object, it should block the `inbox` queue using
:py:func:`wishbone.tools.WishboneQueue.putLock` since it makes no sense to
allow events to come into the module  since they can't be delivered to the
outside world anyway.
