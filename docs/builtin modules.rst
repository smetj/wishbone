===============
Builtin Modules
===============

Input modules
*************


wishbone.input.amqp
-------------------
.. autoclass:: wishbone.module.amqpin.AMQPIn

--------

wishbone.input.dictgenerator
----------------------------
.. autoclass:: wishbone.module.dictgenerator.DictGenerator

--------

wishbone.input.disk
-------------------
.. autoclass:: wishbone.module.diskin.DiskIn

--------

wishbone.input.gearman
----------------------
.. autoclass:: wishbone.module.gearmanin.GearmanIn

--------

wishbone.input.httpclient
-------------------------
.. autoclass:: wishbone.module.httpinclient.HTTPInClient

--------

wishbone.input.httpserver
-------------------------
.. autoclass:: wishbone.module.httpinserver.HTTPInServer

--------

wishbone.input.namedpipe
------------------------
.. autoclass:: wishbone.module.namedpipein.NamedPipeIn

--------

wishbone.input.pull
-------------------
.. autoclass:: wishbone.module.zmqpullin.ZMQPullIn

--------

wishbone.input.tcp
------------------
.. autoclass:: wishbone.module.tcpin.TCPIn

--------

wishbone.input.testevent
------------------------
.. autoclass:: wishbone.module.testevent.TestEvent

--------

wishbone.input.topic
--------------------
.. autoclass:: wishbone.module.zmqtopicin.ZMQTopicIn

--------

wishbone.input.udp
------------------
.. autoclass:: wishbone.module.udpin.UDPIn


Output modules
**************


wishbone.output.amqp
--------------------
.. autoclass:: wishbone.module.amqpout.AMQPOut

--------

wishbone.output.disk
--------------------
.. autoclass:: wishbone.module.diskout.DiskOut

--------

wishbone.output.elasticsearchout
--------------------------------
.. autoclass:: wishbone.module.elasticsearchout.ElasticSearchOut

--------

wishbone.output.email
---------------------
.. autoclass:: wishbone.module.emailout.EmailOut

--------

wishbone.output.file
--------------------
.. autoclass:: wishbone.module.fileout.FileOut

--------

wishbone.output.http
--------------------
.. autoclass:: wishbone.module.httpoutclient.HTTPOutClient

--------

wishbone.output.null
--------------------
.. autoclass:: wishbone.module.null.Null

--------

wishbone.output.push
--------------------
.. autoclass:: wishbone.module.zmqpushout.ZMQPushOut

--------

wishbone.output.sse
-------------------
.. autoclass:: wishbone.module.sse.ServerSentEvents

--------

wishbone.output.stdout
----------------------
.. autoclass:: wishbone.module.stdout.STDOUT

--------

wishbone.output.syslog
----------------------
.. autoclass:: wishbone.module.wbsyslog.Syslog

--------

wishbone.output.tcp
-------------------
.. autoclass:: wishbone.module.tcpout.TCPOut

--------

wishbone.output.topic
---------------------
.. autoclass:: wishbone.module.zmqtopicout.ZMQTopicOut

--------

wishbone.output.udp
-------------------
.. autoclass:: wishbone.module.udpout.UDPOut

--------

wishbone.output.UDSOut
----------------------
.. autoclass:: wishbone.module.udsout.UDSOut


Flow modules
************

wishbone.flow.consensus
-----------------------
.. autoclass:: wishbone.module.consensus.Consensus

--------

wishbone.flow.funnel
--------------------
.. autoclass:: wishbone.module.funnel.Funnel

--------

wishbone.flow.fanout
--------------------
.. autoclass:: wishbone.module.fanout.Fanout

--------

wishbone.flow.match
-------------------
.. autoclass:: wishbone.module.match.Match

--------

wishbone.flow.roundrobin
------------------------
.. autoclass:: wishbone.module.roundrobin.RoundRobin


Function modules
****************

wishbone.function.header
------------------------
.. autoclass:: wishbone.module.header.Header

--------

wishbone.funtion.validatejson
-----------------------------
.. autoclass:: wishbone.module.jsonvalidate.JSONValidate

--------

wishbone.function.keyvalue
--------------------------
.. autoclass:: wishbone.module.keyvalue.KeyValue

--------

wishbone.function.loglevelfilter
--------------------------------
.. autoclass:: wishbone.module.loglevelfilter.LogLevelFilter

--------

wishbone.function.template
--------------------------
.. autoclass:: wishbone.module.template.Template



Encode modules
**************

wishbone.encode.graphite
------------------------
.. autoclass:: wishbone.module.graphite.Graphite

--------

wishbone.encode.humanlogformat
------------------------------
.. autoclass:: wishbone.module.humanlogformat.HumanLogFormat

--------

wishbone.encode.influxdb
------------------------
.. autoclass:: wishbone.module.influxdb.InfluxDB

--------

wishbone.encode.json
--------------------
.. autoclass:: wishbone.module.jsonencode.JSONEncode

--------

wishbone.encode.msgpack
-----------------------
.. autoclass:: wishbone.module.msgpackencode.MSGPackEncode



Decode modules
**************

wishbone.decode.json
--------------------
.. autoclass:: wishbone.module.jsondecode.JSONDecode

--------

wishbone.decode.msgpack
-----------------------
.. autoclass:: wishbone.module.msgpackdecode.MSGPackDecode

