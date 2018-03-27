Version 3.1.2
=============

Features:

    - Changed requirement where in case of Input modules, the ``ActorConfig``
      ``protocol`` parameter should get a function returning a new instance of
      ``decode.handler()``. Input modules should create for each concurrent
      incoming data stream a new protocol decoder instance using the
      ``wishbone.module.InputModule.getDecoder()`` method.
