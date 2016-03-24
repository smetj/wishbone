===============
Builtin Modules
===============

Input modules
*************

wishbone.input.amqp
-------------------
.. autoclass:: wishbone.module.amqpin.AMQPIn

--------

wishbone.input.cron
-------------------------
.. autoclass:: wishbone.module.cron.Cron

--------

wishbone.input.dictgenerator
----------------------------
.. autoclass:: wishbone.module.dictgenerator.DictGenerator

--------

wishbone.input.disk
-------------------
.. autoclass:: wishbone.module.diskin.DiskIn

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

wishbone.input.tcp
------------------
.. autoclass:: wishbone.module.tcpin.TCPIn

--------

wishbone.input.testevent
------------------------
.. autoclass:: wishbone.module.testevent.TestEvent

--------

wishbone.input.udp
------------------
.. autoclass:: wishbone.module.udpin.UDPIn

--------

wishbone.input.zeromq_pull
--------------------------
.. autoclass:: wishbone.module.zmqpullin.ZMQPullIn

--------

wishbone.input.zeromq_topic
---------------------------
.. autoclass:: wishbone.module.zmqtopicin.ZMQTopicIn



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

wishbone.output.udp
-------------------
.. autoclass:: wishbone.module.udpout.UDPOut

--------

wishbone.output.UDSOut
----------------------
.. autoclass:: wishbone.module.udsout.UDSOut

--------

wishbone.output.zeromq_topic
----------------------------
.. autoclass:: wishbone.module.zmqtopicout.ZMQTopicOut

--------

wishbone.output.zeromq_push
---------------------------
.. autoclass:: wishbone.module.zmqpushout.ZMQPushOut



Flow modules
************

wishbone.flow.funnel
--------------------
.. autoclass:: wishbone.module.funnel.Funnel

--------

wishbone.flow.fanout
--------------------
.. autoclass:: wishbone.module.fanout.Fanout

--------

wishbone.input.fresh
-------------------
.. autoclass:: wishbone.module.fresh.Fresh

--------

wishbone.flow.roundrobin
------------------------
.. autoclass:: wishbone.module.roundrobin.RoundRobin

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

wishbone.function.deserialize
-----------------------------
.. autoclass:: wishbone.module.deserialize.Deserialize

--------

wishbone.function.modify
------------------------
.. autoclass:: wishbone.module.modify.Modify

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

wishbone.encode.humanlogformat
------------------------------
.. autoclass:: wishbone.module.humanlogformat.HumanLogFormat

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

