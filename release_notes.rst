Version 3.1.5
=============

Changes:

    - Introduced `wishbone.queue.QueuePool` object to simplify queue
      management outside of the Actor in preparation of using different queue
      Types.

    - Introduced `wishbone.queue.MemoryQueue` the default Wishbone queue type.

    - Modified `wishbone.actor.Actorconfig` object signature to pass the
      `wishbone.queue.QueuePool` object instance to it.

    - When connecting two queues we are no long overwriting one instance with
      the other but we are actually shoveling messages from one queue to the
      other using a greenthread.

