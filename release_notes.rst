Version 3.1.1
=============

Bugfixes:

    - remove closing of stdout filehandle as it might lead to stacktraces when
      its still required. Leave it as is.

Features:

    - Changed behaviour of Actor.setEncoder and Actor.setDecoder so they don't
      override the referred encoder/decoder when one is already setup through
      ActorConfig.
