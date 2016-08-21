======
Events
======



    *wishbone.event.Event object instances are used to store and transport structured data
    between module queues.*


The `input modules`_ should initialize a :py:class:`wishbone.event.Event` instance to
encapsulate the data they receive or generate.

:py:class:`wishbone.event.Event` is a simple class used for data representation
including some convenience functions for data manipulation.

**Examples**

.. code:: python

    >>> from wishbone.event import Event
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

.. toctree::
    bulk_events/index

.. _input modules: module%20types.html#input-modules
