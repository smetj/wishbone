============
Introduction
============

.. note::

    Wishbone currently uses Gevent.  The modules run as cooperatively
    scheduled greenlets while taking advantage of the cooperative socket
    support for network IO.  This makes Wishbone servers cope best with IO
    bound tasks.

Modules and Queues
------------------

Modules are `greenlets`_ each with their own specific functionality. They are
created by inheriting :py:class:`wishbone.Actor` as a baseclass. Modules
cannot and are not supposed to directly invoke each others functionality.
Their only means of interaction is by passing :py:class:`wishbone.event.Event`
objects to each other's :py:class:`wishbone.Queue` queues.

Modules typically have, but are **not** limited to, an **inbox**, **outbox**,
**success** and **failed** queue.

.. warning::

    When a queue is not connected to another queue then submitting a message
    into it will result into the message being dropped.  This is by design to
    ensure queues do not fill up without ever being consumed.


Router
------

The :py:class:`wishbone.router.Default` object loads and initializes the
modules defined in the bootstrap file.  It is responsible for setting up the
module queue connections.

By default, the router connects each module's *metrics* and *logs* queue to a
:py:class:`wishbone.module.Funnel` named **wishbone_metrics** and
**wishbone_logs** respecively.  It's up to user to further organize log and
metric processing by connecting other modules to one of these instances.

If wishbone is started in debug mode and queue **wishbone_logs** isn't
connected to another queue then the router will connect the **wishbone_logs**
module instance to a :py:class:`wishbone.module.HumanLogFormat` module
instance which on its turn is connected to a
:py:class:`wishbone.module.STDOUT` module instance.


Events
------

:py:class:`wishbone.event.Event` instances are used to transport data between modules.

The `input modules`_ should initialize a :py:class:`wishbone.event.Event` instance to
encapsulate the data they receive or generate.

:py:class:`wishbone.event.Event` is a simple class used for data representation
:including some convenience functions for data manipulation.

Examples
~~~~~~~~

.. code:: python

    >>> from wishbone.event.Event import Event
    >>> e = Event("hi")
    >>> e.dump()
    {'@timestamp': '2015-12-13T10:45:35.442088+01:00', '@version': 1, '@data': 'hi'}
    >>>

Initializing the Event objects assigns the data you pass to *@data*.


.. code:: python

    >>> e = Event("hi")
    >>> e.get()
    'hi'
    >>>

By default, the get method returns *@data*.


.. code:: python

    >>> e = Event({"one": {"two": hi}})
    >>> e.get('@data.one.two')
    'hi'
    >>>

Nested dictionaries can be accessed in dotted format.


.. code:: python

    >>> e = Event('hi')
    >>> e.set("howdy", "one.two.three")
    >>> e.get('one')
    {'two': {'three': 'howdy'}}
    >>>

New 'root' keys can be created outside @data.
Setting nested dictionary values can be done using dotted format.


.. code:: python

    >>> e = Event('hello')
    >>> e.dump(complete=True)
    {'@timestamp': '2015-12-13T11:10:45.862036+01:00', '@tmp': {},
    '@version': 1, '@data': 'hello', '@errors': {}}
    >>>>

- *@tmp* is where modules can optionally store temporary data which is not
  part of the data model but contain useful information for other modules.

- The *@errors* key is where modules store exceptions related information.


.. autoclass:: wishbone.event.Event
    :members:



.. _executable: cli%20options.html
.. _builtin modules: builtin%20modules.html
.. _input modules: builtin%20modules.html#input-modules
.. _output modules: builtin%20modules.html#output-modules
.. _greenlets: https://greenlet.readthedocs.org/en/latest/