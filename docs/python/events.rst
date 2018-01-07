:orphan:

======
Events
======
.. _events:

    *wishbone.event.Event object instances are used to store and transport structured data
    between module queues.*


:ref:`Input <input>` modules should initialize a :py:class:`wishbone.event.Event` instance to
encapsulate the data they receive or generate.

:py:class:`wishbone.event.Event` is a simple class used for data representation
including some convenience functions for data manipulation.

An event contains following fields:

.. code:: javascript

    {
      "cloned": false,
      "bulk": false,
      "data": "hi",
      "errors": {},
      "tags": [],
      "timestamp": 1505650508.6642358,
      "tmp": {},
      "ttl": 254,
      "uuid_previous": [],
      "uuid": "e921e9ba-20d4-4245-bdb6-1913e7ae24e4"
    }



* ``cloned`` If the event has been cloned using
  :func:`wishbone.event.Event.clone` this field of the cloned event will be
  set to ``true``.  Along with this the uuid of the original event will be
  added to the ``uuid_previous`` field.

* ``bulk`` If the event is initialized as a bulk event then this value is set
  to `true`.

* ``data`` Contains the actual payload of the event.  All of the events data
  resides here.

* ``errors`` A dict containing errors produced by modules.

* ``tags`` A list containing tags.

* ``timestamp`` An *epoch* timestamp when the event was created.

* ``tmp`` A space for modules to store temporary data potentially useful for
  other modules.

* ``ttl`` The TTL value of the event.  Each time an event passes a module the
  TTL value is decremented until the event expires.

* ``uuid_previous`` A list containing the UUIDs of the events from which the
  current event is cloned.  Useful to track an event's origin.

* ``uuid`` Each event gets a UUID when created.


Examples
--------

Initializing the Event objects assigns the data you pass to *data*.

.. code:: python

    >>> from wishbone.event import Event
    >>> e = Event("hi")
    >>> e.dump()
    {'cloned': False, 'bulk': False, 'data': 'hi', 'errors': {}, 'tags': [], 'timestamp': 1505650508.6642358, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': 'e921e9ba-20d4-4245-bdb6-1913e7ae24e4'}
    >>>


----

By default, the get method returns *data*.

.. code:: python

    >>> e = Event("hi")
    >>> e.get()
    'hi'
    >>> e.get("data")
    'hi'
    >>>


----

Nested dictionaries can be accessed in dotted format.

.. code:: python

    >>> e = Event({"one": {"two": hi}})
    >>> e.get('data.one.two')
    'hi'
    >>>


----

New 'root' keys can be created outside data.
Setting nested dictionary values can be done using dotted format.

.. code:: python

    >>> e = Event('hi')
    >>> e.set("howdy", "one.two.three")
    >>> e.get('one')
    {'two': {'three': 'howdy'}}
    >>>


----

Dumping the event into a data structure makes it easy to serialize it to
another format, ship it outside Wishbone and convert it again into an actual
:py:class:`wishbone.event.Event` instance.


.. code:: python

    >>> event_dump = Event("hello").dump()
    >>> event_dump
    {'cloned': False, 'bulk': False, 'data': 'hello', 'errors': {}, 'tags': [], 'timestamp': 1505653186.98964, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '53a2a3b5-52f0-4ba5-b991-388e27fc75f2'}
    >>> event = Event().slurp(event_dump)
    >>> event.dump()
    {'cloned': False, 'bulk': False, 'data': 'hello', 'errors': {}, 'tags': [], 'timestamp': 1505653204.6875052, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '53a2a3b5-52f0-4ba5-b991-388e27fc75f2'}
    >>>


----

:func:`wishbone.event.Event.render` allows you to provide a `Jinja2` template
string which will be returned rendered using the data of the event itself.


.. code:: python

    >>> e = Event({"one":1})
    >>> e.render('{{data.one}} is a number stored in the event with UUID {{uuid}}')
    '1 is a number stored in the event with UUID ceb28f1f-a377-4182-841a-e01ed11cb668'
    >>>


----

Cloning events keeps track of the previous UUIDs in order to track an event's origin.

.. code:: python

    >>> from wishbone.event import Event
    >>> event_1 = Event("hello")
    >>> event_1.dump()
    {'cloned': False, 'bulk': False, 'data': 'hello', 'errors': {}, 'tags': [], 'timestamp': 1505652258.0975654, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '1b1e28a5-9ec7-484d-98db-4b645e69363a'}
    >>> event_2 = event_1.clone()
    >>> event_2.dump()
    {'cloned': True, 'bulk': False, 'data': 'hello', 'errors': {}, 'tags': [], 'timestamp': 1505652301.2712455, 'tmp': {}, 'ttl': 254, 'uuid_previous': ['1b1e28a5-9ec7-484d-98db-4b645e69363a'], 'version': 1, 'uuid': '2caf2e0d-d2ec-4ced-ad82-c69859c450ed'}
    >>> event_3 = event_2.clone()
    >>> event_3.dump()
    {'cloned': True, 'bulk': False, 'data': 'hello', 'errors': {}, 'tags': [], 'timestamp': 1505652318.7972248, 'tmp': {}, 'ttl': 254, 'uuid_previous': ['1b1e28a5-9ec7-484d-98db-4b645e69363a', '2caf2e0d-d2ec-4ced-ad82-c69859c450ed'], 'version': 1, 'uuid': '4b6525ef-e03a-4bd4-86ef-99f6c8cc4a03'}


Bulk Events
-----------
.. _bulk_events:

.. note::

    *output* modules mainly use Bulk events in order to submit multipe events at once.


Bulk events are made by initializing :class:`wishbone.event.Event` with `bulk`
set to `True`.

Bulk events store other events in *dumped* format in a simple list under `data`.

Example:

.. code:: python

  >>> from wishbone.event import Event
  >>> from wishbone.event import extractBulkItems
  >>>
  >>> e = Event(bulk=True)
  >>> e.appendBulk(Event({"one":1}))
  >>> e.appendBulk(Event({"two":2}))
  >>> e.appendBulk(Event({"three":3}))
  >>> e.dump()
  {'cloned': False, 'bulk': True, 'data': [{'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1505674274.242459, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '0469f2f6-2e1e-4f54-bc9d-01d926a31c5f'}, {'cloned': False, 'bulk': False, 'data': {'two': 2}, 'errors': {}, 'tags': [], 'timestamp': 1505674274.2428124, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '9d193329-6ad6-468a-ab53-4989c36627a3'}, {'cloned': False, 'bulk': False, 'data': {'three': 3}, 'errors': {}, 'tags': [], 'timestamp': 1505674274.242997, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': 'a203ff10-4361-41c2-b5e5-bee7075ecf4d'}], 'errors': {}, 'tags': [], 'timestamp': 1505674274.2423306, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '15887953-51ad-437f-af51-2bc9d99681a3'}
  >>> for item in extractBulkItems(e):
  ...     print(item.dump())
  ...
  {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1505674275.5071478, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '0469f2f6-2e1e-4f54-bc9d-01d926a31c5f'}
  {'cloned': False, 'bulk': False, 'data': {'two': 2}, 'errors': {}, 'tags': [], 'timestamp': 1505674275.50755, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': '9d193329-6ad6-468a-ab53-4989c36627a3'}
  {'cloned': False, 'bulk': False, 'data': {'three': 3}, 'errors': {}, 'tags': [], 'timestamp': 1505674275.5078042, 'tmp': {}, 'ttl': 254, 'uuid_previous': [], 'version': 1, 'uuid': 'a203ff10-4361-41c2-b5e5-bee7075ecf4d'}
  >>>


.. _input modules: module%20types.html#input-modules
