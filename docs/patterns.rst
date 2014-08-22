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
using :py:func:`wishbone.router.Default.registerModule`.

So when registering a module like this:

.. code-block:: python

    router = Default(interval=1)
    router.registerModule(STDOUT, "on_screen")

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

Handle failed and successful events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output modules are responsible of delivering messages to the outside world.
Obviously, we want this to happen as reliable as possible. Whenever the
function registered with py:class:`wishbone.Actor.registerConsumer` fails to
submit the event to the outside world and because of that raises an exception,
then Wishbone will submit the event to the module's **failed** queue.

On the contrary, whenever the function registered with
py:class:`wishbone.Actor.registerConsumer` exits successfully the event is
submitted to the module's **successful** queue.

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

