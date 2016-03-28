============
Module types
============

Wishbone has 6 different module types builtin.

Input modules
-------------

`Input modules`_ take data in from the outside world into the Wishbone
framework.

Features:

* Creates :py:class:`wishbone.event.Event` instances from data.
* Place events into its **outbox** queue.


Output modules
--------------

`Output modules`_ submit data to an external service.

Features:

* *output* modules should have a *selection* parameter defaulting to *'@data'*
  which defines the part of the event which is actually submitted to   the
  external service.

* Should inspect each incoming event whether it is of type
  :py:class:`wishbone.event.Event` or :py:class:`wishbone.event.Bulk` and
  handle bulk events accordingly.

Flow modules
------------

`Flow modules`_ apply logic on incoming messages to determine which queue to
`submit the data to.  They do not really alter events in transit.

Features:

* Do not alter events in transit.


Encode modules
--------------

`Encode modules`_ convert:

* a Python data structure stored in :py:class:`wishbone.event.Event`
* :py:class:`wishbone.event.Metric`
* :py:class:`wishbone.event.Log`

 into another data format.

Features:

* Typically have an *inbox* and *outbox* queue.


Decode modules
--------------

`Decode modules`_ convert some format into either:

* a Python data structure stored in :py:class:`wishbone.event.Event`
* :py:class:`wishbone.event.Metric`
* :py:class:`wishbone.event.Log`

Features:

* Typically have an *inbox* and *outbox* queue.


Function modules
----------------

`Function modules`_ alter events in transit

Features:

* Typically have an *inbox* and *outbox* queue.


.. _Input modules: builtin%20modules.html#input-modules
.. _Output modules: builtin%20modules.html#output-modules
.. _Flow modules: builtin%20modules.html#flow-modules
.. _Encode modules: builtin%20modules.html#encode-modules
.. _Decode modules: builtin%20modules.html#decode-modules
.. _Function modules: builtin%20modules.html#function-modules
.. _creates: events.html
