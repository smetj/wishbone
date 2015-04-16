===============
Builtin Modules
===============

Input modules
*************


wishbone.input.amqp
-------------------
.. autoclass:: wishbone.module.AMQPIn

--------

wishbone.input.dictgenerator
----------------------------
.. autoclass:: wishbone.module.DictGenerator

--------

wishbone.input.disk
-------------------
.. autoclass:: wishbone.module.DiskIn

--------

wishbone.input.gearman
----------------------
.. autoclass:: wishbone.module.GearmanIn

--------

wishbone.input.httpclient
-------------------------
.. autoclass:: wishbone.module.HTTPInClient

--------

wishbone.input.httpserver
-------------------------
.. autoclass:: wishbone.module.HTTPInServer

--------

wishbone.input.namedpipe
-------------------------
.. autoclass:: wishbone.module.NamedPipeIn

--------

wishbone.input.pull
-------------------------
.. autoclass:: wishbone.module.ZMQPullIn

--------

wishbone.input.tcp
-------------------------
.. autoclass:: wishbone.module.TCPIn

--------

wishbone.input.testevent
-------------------------
.. autoclass:: wishbone.module.TestEvent

--------

wishbone.input.topic
-------------------------
.. autoclass:: wishbone.module.ZMQTopicIn

--------

wishbone.input.udp
-------------------------
.. autoclass:: wishbone.module.UDPIn


Output modules
**************


wishbone.output.amqp
--------------------
.. autoclass:: wishbone.module.AMQPOut

--------

wishbone.output.disk
--------------------
.. autoclass:: wishbone.module.DiskOut

--------

wishbone.output.file
--------------------
.. autoclass:: wishbone.module.FileOut

--------

wishbone.output.http
--------------------
.. autoclass:: wishbone.module.HTTPOutClient

--------

wishbone.output.null
--------------------
.. autoclass:: wishbone.module.Null

--------

wishbone.output.topic
---------------------
.. autoclass:: wishbone.module.ZMQTopicOut

--------

wishbone.output.sse
-------------------
.. autoclass:: wishbone.module.ServerSentEvents

--------

wishbone.output.stdout
----------------------
.. autoclass:: wishbone.module.STDOUT

--------

wishbone.output.syslog
----------------------
.. autoclass:: wishbone.module.Syslog

--------

wishbone.output.tcp
-------------------
.. autoclass:: wishbone.module.TCPOut

--------

wishbone.output.push
--------------------
.. autoclass:: wishbone.module.ZMQPushOut

--------

wishbone.output.udp
-------------------
.. autoclass:: wishbone.module.UDPOut

--------

wishbone.output.UDSOut
----------------------
.. autoclass:: wishbone.module.UDSOut


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

wishbone.flow.match
--------------------
.. autoclass:: wishbone.module.Match

--------

wishbone.flow.roundrobin
------------------------
.. autoclass:: wishbone.module.RoundRobin


Function modules
****************

wishbone.function.header
------------------------
.. autoclass:: wishbone.module.Header

--------

wishbone.function.template
--------------------------
.. autoclass:: wishbone.module.Template

wishbone.funtion.validatejson
-----------------------------
.. autoclass:: wishbone.module.JSONValidate


Encode modules
**************

wishbone.encode.graphite
------------------------
.. autoclass:: wishbone.module.Graphite

--------

wishbone.encode.humanlogformat
------------------------------
.. autoclass:: wishbone.module.HumanLogFormat

--------

wishbone.encode.msgpack
-----------------------
.. autoclass:: wishbone.module.MSGPackEncode

--------

wishbone.encode.json
-----------------------
.. autoclass:: wishbone.module.JSONEncode


Decode modules
**************

wishbone.decode.msgpack
-----------------------
.. autoclass:: wishbone.module.MSGPackDecode

--------

wishbone.decode.json
-----------------------
.. autoclass:: wishbone.module.JSONDecode