===============
Builtin Modules
===============

Input modules
*************

wishbone.input.disk
-------------------
.. autoclass:: wishbone.module.DiskIn

--------

wishbone.input.testevent
------------------------
.. autoclass:: wishbone.module.TestEvent

--------

wishbone.input.tcp
------------------
.. autoclass:: wishbone.module.TCPIn

--------

wishbone.input.amqp
-------------------
.. autoclass:: wishbone.module.AMQPIn


wishbone.input.dictgenerator
----------------------------
.. autoclass:: wishbone.module.DictGenerator


wishbone.input.topic
----------------------------
.. autoclass:: wishbone.module.ZMQTopicIn


Output modules
**************


wishbone.output.disk
--------------------
.. autoclass:: wishbone.module.DiskOut

--------

wishbone.output.amqp
--------------------
.. autoclass:: wishbone.module.AMQPOut

--------

wishbone.output.stdout
----------------------
.. autoclass:: wishbone.module.STDOUT

--------

wishbone.output.tcp
-------------------
.. autoclass:: wishbone.module.TCPOut

--------

wishbone.output.syslog
----------------------
.. autoclass:: wishbone.module.Syslog

--------

wishbone.output.null
--------------------
.. autoclass:: wishbone.module.Null

--------

wishbone.output.topic
-------------------------
.. autoclass:: wishbone.module.ZMQTopicOut


Flow modules
************


wishbone.flow.funnel
--------------------
.. autoclass:: wishbone.module.Funnel

--------

wishbone.flow.fanout
--------------------
.. autoclass:: wishbone.module.Fanout

--------

wishbone.flow.roundrobin
------------------------
.. autoclass:: wishbone.module.RoundRobin


Function modules
****************

wishbone.function.header
------------------------
.. autoclass:: wishbone.module.header


Encode modules
**************

wishbone.encode.graphite
------------------------
.. autoclass:: wishbone.module.Graphite


wishbone.encode.humanlogformat
------------------------------
.. autoclass:: wishbone.module.HumanLogFormat


wishbone.encode.msgpack
-----------------------
.. autoclass:: wishbone.module.MSGPackEncode


Decode modules
**************

wishbone.decode.msgpack
-----------------------
.. autoclass:: wishbone.module.MSGPackDecode