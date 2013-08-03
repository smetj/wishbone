Wishbone changelog
==================

Version 0.4
~~~~~~~~~~~

- Complete rewrite of all components.
- Queues offer more functionality like locking, statistics.
- Better gevent aware locking mechanisms.
- Possibility to lock/unlock queues based on upstream throughput.
- Metrics endpoint can be connected to regular pipe structure.
- Logs endpoint can be connected to regular pipe structure.
- Bootstrap files in YAML format.
- Wisbone categories: flow, logging, metrics, function, input, output
- Definable gevent context switch when looping.

Version 0.32
~~~~~~~~~~~~

- Enforce JSON validate Draft3 when a recent version of jsonschema is
  installed.
- Fixed bug issuing "Exception KeyError" on exit.
- Verify if a config file is provided and if not return a useful error.
- Autocreate queue when submitting message to non existing queue.

Version 0.31
~~~~~~~~~~~~

- Updated Gevent dependency_links in setup.py to the new Github page.
- Adding many missing dependencies to setup.py
- Added check to setup.py to verify expected daemon version.
- Added a built in profiler version based on gevent_profiler.
- Fixed bug to make Wisbone execute stop() method of modules.
- Fixed bug producing stacktrace on exit.
- Allowing string, integer, boolean and array data types for variable values.

Version 0.30
~~~~~~~~~~~~

- Switched to better performing egenix mx-base queues.
