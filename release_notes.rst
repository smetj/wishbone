Version 3.1.1
=============

Bugfixes:

    - remove closing of stdout filehandle as it might lead to stacktraces when
      its still required. Leave it as is.

    - Fixed wishbone.protocol.decoder problems when exceeding allowed buffer.

Features:

    - Changed behaviour of Actor.setEncoder and Actor.setDecoder so they don't
      override the referred encoder/decoder when one is already setup through
      ActorConfig.

    - Changed requirement where in case of Input modules, the ``ActorConfig``
      ``protocol`` parameter should get a function returning a new instance of
      ``decode.handler()``. Input modules should create for each concurrent
      incoming data stream a new protocol decoder instance using the
      ``wishbone.module.InputModule.getDecoder()`` method.



