=======
Process
=======
.. _process:

.. note::

    Process modules process and therefor modify events in one way or another.

The builtin Wishbone Output modules:

+----------------------------------------------------------------------------------+------------------------------------------+
| Name                                                                             | Description                              |
+==================================================================================+==========================================+
| :py:class:`wishbone.module.process.modify <wishbone.module.modify.Modify>`       | Modify and manipulate datastructures.    |
+----------------------------------------------------------------------------------+------------------------------------------+
| :py:class:`wishbone.module.process.pack <wishbone.module.pack.Pack>`             | Packs multiple events into a bulk event. |
+----------------------------------------------------------------------------------+------------------------------------------+
| :py:class:`wishbone.module.process.template <wishbone.module.template.Template>` | Renders Jinja2 templates.                |
+----------------------------------------------------------------------------------+------------------------------------------+
| :py:class:`wishbone.module.process.unpack <wishbone.module.unpack.Unpack>`       | Unpacks bulk events into single events.  |
+----------------------------------------------------------------------------------+------------------------------------------+


-----

``Process`` modules must base :py:class:`wishbone.module.ProcessModule`:

.. autoclass:: wishbone.module.ProcessModule
    :members:
    :show-inheritance:
    :inherited-members:




