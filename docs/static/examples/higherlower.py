#!/usr/bin/env python

from wishbone.module import FlowModule


class HigherLower(FlowModule):
    '''
    **Checks whether an integer is higher or lower than the defined value.**

    Checks whether an event value is higher, lower or equal to the defined baseline.
    Depending on the outcome, the event will be submitted to the appropirate queue.

    Parameters::

        - base(int)(100)
           |  The value to compare against.

        - value(int)(100)
           |  The value to compare.

    Queues::

        - inbox
           |  Incoming messages

        - higher
           |  Events with a higher value than ``value`` are submitted to this
           |  queue.

        - lower
           |  Events with a lower value than ``value`` are submitted to this
           |  queue.

        - equal
           |  Events with an equal value to ``value`` are submitted to this
           |  queue.
    '''

    def __init__(self, actor_config, base=100, value=100):
        FlowModule.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("higher")
        self.pool.createQueue("lower")
        self.pool.createQueue("equal")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        if not isinstance(event.data, int):
            raise TypeError("Event data is not type integer")

        if event.kwargs.value > event.kwargs.base:
            self.submit(event, self.pool.queue.higher)
        elif event.kwargs.value < event.kwargs.base:
            self.submit(event, self.pool.queue.lower)
        else:
            self.submit(event, self.pool.queue.equal)
