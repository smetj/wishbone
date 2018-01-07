======
Decode
======
.. _decode:

Decode modules can only be used by :ref:`input <input>` modules.  They are
reponsible for converting the incoming data format into a format Wisbone can
work with.

Some characteristings:

* Decoder modules should base :py:class:`wishbone.protocol.Decode`

Wishbone comes with following protocol decoders:

+-----------------------------------------------------------------------------------------+----------------------------------------------------+
| Name                                                                                    | Description                                        |
+=========================================================================================+====================================================+
| :py:class:`wishbone.protocol.decode.plain <wishbone.protocol.decode.plain.Plain>`       | Decode plaintext using the defined charset.        |
+-----------------------------------------------------------------------------------------+----------------------------------------------------+
| :py:class:`wishbone.protocol.decode.json <wishbone.protocol.decode.json.JSON>`          |  Decode JSON data into a Python data structure.    |
+-----------------------------------------------------------------------------------------+----------------------------------------------------+
| :py:class:`wishbone.protocol.decode.msgpack <wishbone.protocol.decode.msgpack.MSGPack>` |  Decode MSGpack data into a Python data structure. |
+-----------------------------------------------------------------------------------------+----------------------------------------------------+


See following examples:

* :ref:`Using a protocol decoder. <using_a_protocol_decoder>`

