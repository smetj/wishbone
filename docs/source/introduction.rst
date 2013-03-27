============
Introduction
============

A Wishbone event pipeline setup typically receives data from some external source such as an UDP server or a message broker like RabbitMQ.  The incoming data then travels a set of modules, each with a specific function, after which the data exits to a destination.

Wishbone can bootstrap an event pipeline setups using a configuration file, which allows you to easily alter the configuration of your setup.
The Parallelserver implementation allows you to start, stop and daemonize one or multiple parallel setups using a bootstrap configuration file.

Wishbone modules
================

A Wishbone event pipeline consists out of multiple interconnected modules.  Each module is a functionally isolated block of code which preferably does only 1 thing.
Each module has at least 2 queues called inbox and outbox.  The modules consume the events arriving in their inbox queue and are put into the outbox queue after processing.
The framework takes care of forwarding the content the outbox queue to the next modules inbox queue.  Modules work independently and asynchronously from each other.

When the modules are loaded into the WishBone and the setup has started then the framework will automatically start the consume the events arriving in the module's inbox and execute the module's consume() function to each message.  It is up to the user to determine when an events needs to be put back into the module's outbox queue.

Although it's not necessarily a strict rule, we could say there are 2 types of modules:

- IOmodules:
 - Receive data from or submit data outside the Wishbone framework.
 - Responsible to convert data coming from the outside into the correct internal Wishbone format.

- Modules:
 - Receive, process and submit events to other modules.

You can find an example for a basic module here:

`<https://github.com/smetj/wishboneModules/blob/master/modules/wb_stdout/wb_stdout/stdout.py>`_

Modules are made available to Wishbone by creating an entrypoint in either the wishbone.module or wishbone.iomodule entrypoint group.
Here you can find an example setup.py which installs a module and adds an entrypoint for Wishbone to work with:

`<https://github.com/smetj/wishboneModules/blob/master/modules/wb_stdout/setup.py>`_

You can use the "list" server command to list all modules available to Wishbone.


Routing
-------

The path an events takes inside the event pipeline is determined by connecting the messages queues of the different modules to each other.  Not every event needs to follow the same path.  Modules have by default 2 queues: inbox and outbox.  A user can choose to add a number of custom queues to the module which allows more complex routing setups.

Possible connections are:

- 1-1 	: The most standard connection. Events from 1 queue go into another queue.
- 1-n	: 1 to many connection.  This duplicates the events from 1 queue to each queue it is connected to.
- n-1	: Many to one connection.  This writes the events of many queues into 1 queue. (not implemented yet)

The path an event travels is determined by the "routingtable" in the bootstrap file.
By connecting the queues of different modules to each other, youe can make a clean workflow.

Events
------

Data coming into one of the "IO modules" is in whatever format. The moment data leaves the IO module it should have the right format:

.. code-block:: python
    
    {'headers':{},'data':data}


.. warning::

	The moment Wishbone shovels an event from one queue to the other it will drop the event if it doesn't have the right format.


ParallelServer
==============

:class:`wishbone.server.ParallelServer` is a convenience class which has 3 functions:

Process handling and parallelisation.
-------------------------------------

:class:`wishbone.server.ParallelServer` takes care of the starting, stopping and daemonizing of a Wishbone setup.
Besides that it also takes care of starting multiple parallel instances when required.
Having more than one instance means there is a libevent loop per process.

Argument parsing.
-----------------

:class:`wishbone.server.ParallelServer` takes care of parsing the command line arguments required to bootstrap a Wishbone setup.

.. code-block:: text
        
        [vagrant@sandbox broker]$ ./brokertest
        BrokerTest version 0.1                                          Jelle Smet

        This setup generates a feedback loop to the RabbitMQ message broker.

        /usr/bin/brokertest command --config file [--instances number] [--loglevel level] [--pid filename] [--group groupname]


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
                            The default value is /tmp/PySeps.pid
            
            --group         The name of the module group to list modules from.
                            

                     
                                      
            Support: https://groups.google.com/forum/?fromgroups=#!forum/python-wishbone

        too few arguments
        
        [vagrant@sandbox broker]$ ./brokertest debug --config brokertest.json --loglevel debug
        2012-11-25 16:38:30,202 INFO Server: Starting BrokerTest in foreground.
        2012-11-25 16:38:30,205 INFO Server: Instance #0 started.
        2012-11-25 16:38:30,208 INFO Server: Started with pids: 3068, 3069
        2012-11-25 16:38:30,280 INFO Broker: Initiated
        2012-11-25 16:38:30,282 INFO Intance #0:loopback: Initiated.
        2012-11-25 16:38:30,314 INFO Intance #0:loopback: Started.
        2012-11-25 16:38:30,314 INFO Broker: Started
        ...

Bootstrapping
-------------

:class:`wishbone.server.ParallelServer` reads the configuration file (using the --config parameter) and starts a setup according to the configuration.
The configuration file (bootstrap file) is in JSON format and consists out of 4 big parts:

- system

  Optional and currently unused.  Reserved for future usage.
  
- metrics  
  
  Contains settings which controls how the internal metrics are handled.

- bootstrap

  Contains which modules to initiate and the parameters which should be used.

- routingtable

  Contains the information of which modules are connected to each other.

For more information see:

:ref:`bootstrapfiles`
