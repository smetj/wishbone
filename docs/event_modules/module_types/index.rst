============
Module types
============

Wishbone has 6 different module types builtin.

Input modules
-------------

    *Input modules read or accept data from the outside world into the
    Wishbone framework.*

Features:

* Creates :py:class:`wishbone.event.Event` instances from data.
* Place events into its **outbox** queue.


Output modules
--------------

    *Output modules write data to the outside world.*

Features:

* *output* modules should have a *selection* parameter defaulting to *'@data'*
  which defines the part of the event which is actually submitted to   the
  external service.

* Should inspect each incoming event whether it is of type
  :py:class:`wishbone.event.Event` or :py:class:`wishbone.event.Bulk` and
  handle bulk events accordingly.

Flow modules
------------

    *Flow modules apply routing logic to passing messages by altering the
    destination queue of the event based on certain properties*

Features:

* Do not alter events in transit.


Encode modules
--------------

    *Encode modules convert the event instance into the requested format*

Features:

* Typically have an *inbox* and *outbox* queue.


Decode modules
--------------

    *Decode modules convert structured data format into the internal event
    respresentation*

Features:

* Typically have an *inbox* and *outbox* queue.


Function modules
----------------

    *Function modules modify events during transit*

Features:

* Typically have an *inbox* and *outbox* queue.


