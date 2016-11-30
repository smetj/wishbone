===============
Builtin Modules
===============

Input modules
*************

wishbone.input.cron
-------------------
.. autoclass:: wishbone.module.cron.Cron

--------

wishbone.input.dictgenerator
----------------------------
.. autoclass:: wishbone.module.dictgenerator.DictGenerator

--------

wishbone.input.testevent
------------------------
.. autoclass:: wishbone.module.testevent.TestEvent


Output modules
**************


wishbone.output.null
--------------------
.. autoclass:: wishbone.module.null.Null

--------

wishbone.output.stdout
----------------------
.. autoclass:: wishbone.module.stdout.STDOUT

--------

wishbone.output.syslog
----------------------
.. autoclass:: wishbone.module.wbsyslog.Syslog


Flow modules
************

wishbone.function.acknowledge
-----------------------------
.. autoclass:: wishbone.module.acknowledge.Acknowledge

--------

wishbone.function.deserialize
-----------------------------
.. autoclass:: wishbone.module.deserialize.Deserialize

--------

wishbone.flow.fanout
--------------------
.. autoclass:: wishbone.module.fanout.Fanout

--------

wishbone.flow.fresh
-------------------
.. autoclass:: wishbone.module.fresh.Fresh

--------

wishbone.flow.funnel
--------------------
.. autoclass:: wishbone.module.funnel.Funnel

--------

wishbone.flow.roundrobin
------------------------
.. autoclass:: wishbone.module.roundrobin.RoundRobin

--------

wishbone.flow.switch
---------------------------
.. autoclass:: wishbone.module.switch.Switch

--------

wishbone.flow.tippingbucket
---------------------------
.. autoclass:: wishbone.module.tippingbucket.TippingBucket

--------

wishbone.flow.ttl
-----------------
.. autoclass:: wishbone.module.ttl.TTL

--------


Function modules
****************

wishbone.function.modify
------------------------
.. autoclass:: wishbone.module.modify.Modify



Encode modules
**************

wishbone.encode.humanlogformat
------------------------------
.. autoclass:: wishbone.module.humanlogformat.HumanLogFormat

--------

wishbone.encode.json
--------------------
.. autoclass:: wishbone.module.jsonencode.JSONEncode

--------

Decode modules
**************

wishbone.decode.json
--------------------
.. autoclass:: wishbone.module.jsondecode.JSONDecode

