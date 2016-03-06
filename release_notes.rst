Wishbone changelog
==================

Version 2.1.2
~~~~~~~~~~~~~

Features:

- Added timeout and redirect support for wishbone.output.

Version 2.1.1
~~~~~~~~~~~~~

Features:

- Added wishbone.input.fresh
- Added support for default value in copy command of wishbone.function.modify
- Added allow_follow and time support to wishbone.input.httpclient
- Added allow_follow and time support to wishbone.output.http

Bugs:

- Misc event data handling bugs.
- Fixed bug in

Version 2.1.0
~~~~~~~~~~~~~

Features:

- New internal data format.
- Adding SO_REUSEPORT for wishbone.input.httpserver
- Allow Logger() to easily monkey patch existing logger calls
- Added --graph option in --debug mode to show layout.
- Added --graph_enable_sys option in --debug mode to switch log
  and metric queue/module inclusion.
- Added support to provide description to the module section of
  the bootstrap file.
- Added support to output modules to select which part of the event
  is submitted externally.
- Added wishbone.flow.jq module which uses jq-lib for JSON pattern matching.
- Added wishbone.function.modify module.
- Added --profile option to profile a wishbone server.

Bugs:

- Fixed bug in "match" module where failed YAML parsing makes the rule
  processing thread die.

Misc:

- Updated to gevent-1.1b6
- Prefixed zeromq modules with 'zeromq_'.
- Rework configuration handling
- Misc performance improvements
- Changed Metric and Log named tuples into Class
- Special funnel modules renamed to '_metrics' and '_logs'.


Version 1.1.1
~~~~~~~~~~~~~

Features:

- Added lock reading rules in wishbone.flow.match module.
- Monkey patching SSL in wishbone.output.http when doing https.
- Better disconnect testing in wishbone.output.tcp
- Workaround for bug in wishbone.function.template where header
  template values are not read correctly when a lookup function
  used.
- Improved logging of jsonvalidate

Bugs:

- Fixed bug in wishbone.function.keyvalue where events got garbled and copied
  multiple times.
- Fixed bug in wishbone.input.amqp where reconnects were not happening.
- Fixed bug where sending logs to logs queue could fill queue and fail with
  QueueFull.
- Fixed bug in metric formatting.

Misc:

- Updated to gevent-1.1b5
- Changed wishbone.output.tcp to open/close connections and do not attempt
  to keep connection open.


Version 1.1.0
~~~~~~~~~~~~~

Features:

- Rewrite new internal event format.
- Refactoring of default router to use ConfigurationManager.
- Refactoring of bootstrap code.
- Support for dynamic and static variable lookups.
- Support for header variable lookups.
- Using ActorConfig object to encapsulate framework specific settings
- Renamed "metrics_funnel" and "logs_funnel" to "wishbone_metrics"
  and "wishbone_logs" respectively.
- New module wishbone.function.keyvalye
- New module wishbone.function.jsonvalidate
- New module wishbone.output.elasticsearch
- New module wishbone.output.http
- New module wishbone.encode.influxdb
- New module wishobne.flow.ttl
- Match module now support negative list membership testing.
- Added support to cancel acknowledgements in wishbone.input.amqp
- Internal queueing now uses standard blocking behavior.
- Changed internal metric format.
- Changed internal log format.
- Reroute wsgi logging to Wishbone logging.
- Adapted modules to use lookups where appropriate.
- Added etcd lookup module.
- Added tests for modules (not complete, more tests required)

Bugfixes:

- Changed matchrule format wishbone.flow.match to allow multiple
  evals on the same key.
- Fix to minimize gethostbyname() lookups in logging.
- Fixed bugs in wishbone.input.amqp
- Fixed bugs in wishbone.output.amqp
- Exceptions are now *always* logged with line number, type, and message.

Version 1.0.3
~~~~~~~~~~~~~

- Fixed dysfunctional wishbone.flow.fanout module.
- Additional queue creation reserved name checking.
- Added deepcopy to wishbone.flow.match module.
- Fix bug in match logic.

Version 1.0.2
~~~~~~~~~~~~~

- Fixed bug in slow amqpin consumption.
- Added wishbone.output.email module.
- diskin and diskout autocreate buffer directory if missing.
- Fixed bug which prevented bootstrapping multiple processes.
- Added more sanity checks on bootstrap file.
- Added wishbone.flow.match module, derived from (and replacement of) PySeps.
- Added wishbone.output.file module.
- Removed incremental number from wishbone.output.disk.
- Fix bug in wishbone.flow.funnel where queuefull was not taken into account.
- Added more bootstrap file verification tests.
- Added wishbone.function.jsonvalidate as a separate daemon.

Version 1.0.1
~~~~~~~~~~~~~

- Make extra module groups to include configurable
  when making a Wishbone based entrypoint.
- Raise proper error when getQueue() requests
  non-existing queue
- Added Gearman input module
- Added SSE (server sent events) output module
- Added LogLevelFilter module
- Fixed bug where --group parameter is ignored by
  list command.
- Fix dependency versions.
- Adding first tests

Version 1.0.0
~~~~~~~~~~~~~

- Complete overhaul of codebase
- Inclusion of external modules
- pep8 all code

Version 0.4.10
~~~~~~~~~~~~~~

- Various log finetuning
- Smaller bugfixes

Version 0.4.9
~~~~~~~~~~~~~

- Make descriptions of modules shorter.
- Header module supports dynamic header generation.
- Fix context switch bug in testevent module

Version 0.4.8
~~~~~~~~~~~~~

- Header module needs a header key.
- Added hostname to internal metric format.
- Fix bug loading syslog, when starting in background.

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
