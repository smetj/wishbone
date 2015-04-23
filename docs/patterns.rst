============================
Patterns and best practices
============================

Handle failed and successful events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output modules are responsible of delivering messages to the outside world.
Obviously, we want this to happen as reliable as possible. Whenever the
function registered with :py:class:`wishbone.Actor.registerConsumer` fails to
submit the event to the outside world and because of that raises an exception,
then Wishbone will submit the event to the module's **failed** queue.

On the contrary, whenever the function registered with
:py:class:`wishbone.Actor.registerConsumer` exits successfully the event is
submitted to the module's **success** queue.

It is up the user to connect these queues to another queue in order come to
the desired strategy.

Whenever these queues remain unconnected, all messages submitted to them are
discarded.

Some practical examples:

- After submitting an event successfully over TCP to the outside world, it is
  submitted to the `successful` queue.  This queue is on its turn connected to
  the AMQP `acknowledge` queue to ascertain it is acknowledged from AMQP.

- After submitting an event over TCP failed, the event is submitted to the
  `failed` queue from where it is forwarded to another module which writes the
  event to disk.

