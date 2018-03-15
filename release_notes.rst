Version 3.1.0
=============


Features:
    - Added wishbone.module.output.throughput
    - Some minor speed improvements prevening useless template rendering where
      string can't be a template.
    - Added debug log showing the module version
    - Fixed docstrings of protocol decode modules
    - Added wishbone.protocol.encode.binary
    - Added parallel streams support for output modules

Changes:

    - Changed ``native_event`` parameter to ``native_events``
    - Added new feature ``parallel_streams`` for output modules
