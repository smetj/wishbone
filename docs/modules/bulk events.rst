===========
Bulk Events
===========

By default events flow one by one from one module the other.
:py:class:`wishbone.event.Bulk` instances contain multiple
:py:class:`wishbone.event.Event` events and therefor can deliver multiple events
at once to a module.

The modules receiving :py:class:`wishbone.event.Bulk` events need to know how to
process them.  By convention, `output modules`_ should know how to deal with
*Bulk* events.

The builtin module :py:class:`wishbone.module.tippingbucket.TippingBucket`
is an example of a module collecting multiple events into a Bulk event and
forwarding it based on one or more conditions.


.. autoclass:: wishbone.event.Bulk
    :members:

.. _output modules: module%20types.html#output-modules
