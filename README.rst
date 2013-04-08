WishBone
========

What?
-----

A Python library to write asynchronous event pipeline servers with minimal
effort.

How?
----

The WishBone Python library offers a framework to write asynchronous event
pipeline servers with minimal effort.  In this context, event pipelines are
best described as a collection of concurrently running modules which consume,
process and produce events. Wishbone module queues are connected to one
another forming a pipeline through which these events travel.  Wishbone
servers can be configured and controlled from from command line using
bootstrap files. Bootstrap files allow to cherry-pick Wishbone modules and to
define how events travel through them.  Multiple identical Wishbone instances
can run as separate processes offering parallel execution.

Installing
----------

Through Pypi:

	$ easy_install wishbone

Or the latest development branch from Github:

	$ git clone git@github.com:smetj/wishbone.git

	$ cd wishbone

	$ sudo python setup.py install


Documentation
-------------
http://smetj.github.com/wishbone/docs/build/html/index.html


Examples
--------

Once Wishbone is installed you can try to execute it:


	[smetj@indigo ~]$ wisbhone
	Wishbone version 0.1                                          	Jelle Smet

	The default Wisbone server.

	/usr/bin/wisbhone command --config file [--instances number] [--loglevel level] [--pid filename] [--group groupname]


	        Commands:

	            start           Starts and daemonizes the program into the background.
	            stop            Stops a daemonized instance.
	            debug           Starts the program in the foreground without detaching.
	            kill            Kills the daemonized instance.
	            list            Lists the available Wishbone modules in group

	        Parameters:

	            --config        The filename of the bootstrap config file.

	            --instances     The number of parallel instances to start. Default is 1.

	            --loglevel      Defines the loglevel to use. Default is "info".
	                            Possible values are:
	                                info, warning, critical, debug

	            --pid           Defines the location of the pidfile.
	                            The default value is /tmp/Wishbone.pid

	            --group         The name of the module group to list modules from.


	Support:

	https://groups.google.com/forum/?fromgroups#!forum/python-wishbone

	too few arguments

	[smetj@indigo ~]$


Using the list command you can check which Wishbone modules you have installed
and available. If you don't have any Wishbone modules installed yet please
visit https://github.com/smetj/wishboneModules

	[smetj@indigo ~]$ wisbhone list

	Available Wishbone modules in group wishbone.iomodule:

	+-----------------+----------------------------------------------------+
	| Entry Point     | Module                                             |
	+-----------------+----------------------------------------------------+
	| UDSServer       | wb_broker.broker:UDSServer                         |
	| Gearmand        | wb_gearmand.gearmand:Gearmand                      |
	| InputGenerator  | wb_inputgenerator.inputgenerator:InputGenerator    |
	| MongoDB         | wb_mongodb.mongodb:MongoDB                         |
	| NamedPipeServer | wb_namedpipeserver.namedpipeserver:NamedPipeServer |
	| TCPClient       | wb_tcpclient.tcpclient:TCPClient                   |
	| UDPServer       | wb_udpserver.udpserver:UDPServer                   |
	| UDSClient       | wb_udsclient.udsclient:UDSClient                   |
	| DictGenerator   | wb_dictgenerator.dictgenerator:DictGenerator       |
	+-----------------+----------------------------------------------------+

	Available Wishbone modules in group wishbone.module:

	+---------------+----------------------------------------------+
	| Entry Point   | Module                                       |
	+---------------+----------------------------------------------+
	| BrokerHeader  | wb_brokerheader.brokerheader:BrokerHeader    |
	| GotMessage    | wb_gotmessage.gotmessage:GotMessage          |
	| JSONValidator | wb_jsonvalidator.jsonvalidator:JSONValidator |
	| Null          | wb_null.null:Null                            |
	| Skeleton      | wb_skeleton.skeleton:Skeleton                |
	| Snappy        | wb_snappy.snappy:Snappy                      |
	| STDOUT        | wb_stdout.stdout:STDOUT                      |
	| TippingBucket | wb_tippingbucket.tippingbucket:TippingBucket |
	+---------------+----------------------------------------------+

	Available Wishbone modules in group wishbone.metrics:

	+-------------+----------------------+
	| Entry Point | Module               |
	+-------------+----------------------+
	| Table       | wb_table.table:Table |
	+-------------+----------------------+

	[smetj@indigo ~]$


Have a look on
https://github.com/smetj/experiments/tree/master/python/wishbone for different
example scenarios.

Support
-------

Drop me an email or post a message on
https://groups.google.com/forum/?fromgroups#!forum/python-wishbone