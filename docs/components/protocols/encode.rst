.. _encode:
======
Encode
======

Encode modules can only be used by :ref:`output <output>` modules.  They are
reponsible for converting the Wishbone internal format into an appropriate outgoing data format.

Some characteristings:

* Encoder modules should base :py:class:`wishbone.protocol.Encode`

Wishbone comes with following protocol decoders:

+-----------------------------------------------------------------------------------------+-----------------------------------+
| Name                                                                                    | Description                       |
+=========================================================================================+===================================+
| :py:class:`wishbone.protocol.encode.json <wishbone.protocol.encode.json.JSON>`          |  Encode data into JSON format.    |
+-----------------------------------------------------------------------------------------+-----------------------------------+
| :py:class:`wishbone.protocol.encode.msgpack <wishbone.protocol.encode.msgpack.MSGPack>` |  Encode data into msgpack format. |
+-----------------------------------------------------------------------------------------+-----------------------------------+


See following examples:

* :ref:`Using a protocol encoder. <using_a_protocol_encoder>`

