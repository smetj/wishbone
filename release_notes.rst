Wishbone changelog
==================

Version 0.4.7
~~~~~~~~~~~~~

- Fix bug which loops disableThrottling().
- Add extra checks on routing table syntax. 
- Added slow output module.
- Fix bug in roundrobin module.
- Update patterns and scenarios documentation.


Version 0.4.6
~~~~~~~~~~~~~

- Cleanup context_switch when looping.
- Add installation documenation.
- Cleanup of throttling functionality.


Version 0.4.5
~~~~~~~~~~~~~

- Fix bug with failing bootstrap


Version 0.4.4
~~~~~~~~~~~~~

- Remove excessive logging.
- Colorize log output in debug mode.
- Add possibility to pause and resuming consuming inside module.
- Use a more generic internal metric format.
- Directly use destination queue in the source module.
- When using context switch, do not actually sleep.
- Removed unused limit parameter when registering a module.


Version 0.4.3
~~~~~~~~~~~~~

- STDOUT module, possibility to print PID
- Improvement: use stdout_logs as instance name when bootstrapping
- Improve error handling when initializing a module with non existent variables
- Improved catching errors when modules do not exist
- Fix bug where modules were not checks if they are registered
- Make sure bootstrap exits with clean error
- Fix bug producer queue was referenced instead of consumer when autocreate
- Add more info to documentation


Version 0.4.2
~~~~~~~~~~~~~

- Fix several bugs load bootstrap files
- Fix bug in fanout module where deepcopy() wasn't used
- Fix bug for misbehaving waitUntilFreePlace()
- Expand documentation
- Added first batch of tests

Version 0.4.1
~~~~~~~~~~~~~

- Include support for throttling.
- Included firsts tests
- Integrate tests in setup.py
- Fix bug where waitUntilFreePlace did not behave correctly when __putLimit()
  was never used.

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
