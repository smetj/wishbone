============================
Patterns and best practices
============================

This section discusses some common usage patterns and best practices. Although
most if not all are strictly spoken not required, they might be helpful in
using Wishbone efficiently.

Modules and event headers
-------------------------

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


Retrieve data from headers
~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Output modules
--------------

Additional queues
~~~~~~~~~~~~~~~~~

Output modules are responsible to deliver messages to the outside world.
Preferably we want this to be done trustworthy.  If submitting events fails we
might need he opportunity for other output modules to take over when desired.
Maybe an input module needs to know whether the event was submitted
successfully by the output modules (Think AMQP).

Although not required from a technical perspective, it might be nice to have
the ability to *optionally* have 2 additional queues to output modules:

    - successful
    - failed

As you might guess, events which have been submitted successfully to the
outside world are then submitted to the *successful* queue and the events
which failed to go out to the *failed* queue.

This behavior can be enabled/disabled during module initialization in order to
define the best strategy required.

Retrying and monitors
~~~~~~~~~~~~~~~~~~~~~