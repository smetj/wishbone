Version 3.1.1
=============

Bugfixes:

    - remove closing of stdout filehandle as it might lead to stacktraces when
      its still required. Leave it as is.
