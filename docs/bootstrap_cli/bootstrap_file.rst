==============
Bootstrap File
==============

A boostrap file is written in YAML syntax and it should adhere `this schema`_.

It consists out of 5 sections:


1. **`protocols`** section:

  .. _bootstrap_protocols:

  This section contains the protocols to initialize.Both protocol instances
  for *input* and *output* modules should be initialized in this section.It's
  not necessary to use all the initialized instances. This section is
  optional.

  A sample extract:

  .. code-block:: yaml

      protocols:
          json_encode:
              protocol: wishbone.protocol.encode.json
              arguments:
                  sort_keys: true
          msgpack_decode:
              protocol: wishbone.protocol.decode.msgpack

  * The ``protocol`` value is the *entrypoint* value.
  * ``arguments`` is optional.


2. **`module_functions`** section:

  .. _bootstrap_module_functions:

  This section initializes the :ref:`module functions <module_functions>`. It
  is not necessary to use all the initialized functions.This section is
  optional.

  A sample extract:

  .. code-block:: yaml

       module_functions:
         tagit:
             function: wishbone.function.module.append
             arguments:
                 data: you_are_tagged
                 destination: tags

  * The ``function`` value is the *entrypoint* name.
  * ``arguments is optional``


3. **`template_functions`** section:

  .. _bootstrap_template_functions:

  This section initializes the :ref:`template functions <template_functions>`.
  It is not necessary to use all the initialized functions.This section is
  optional.


  A sample extract:

  .. code-block:: yaml

       template_functions:
         gimmeNumber:
           function: wishbone.function.template.choice
           arguments:
             array:
               - one
               - two
               - three


  * The ``function`` value is the *entrypoint* name.
  * ``arguments is optional``


4. **`modules`** section:

   .. _bootstrap_modules:

  This section initializes :ref:`modules <modules>`.It is not necessary to
  connect a module to another module in the `routingtable` section. Otherwise
  this section is mandatory.

  A sample extract:

  .. code-block:: yaml

       modules:
         input:
           module: wishbone.module.input.generator
           arguments:
             interval: 1
             payload: hello

         output:
           module: wishbone.module.output.stdout
           arguments:
             prefix: '{{ data }} is the prefix '
             selection: '.'


  * The ``module`` value is the entrypoint name.
  * ``arguments`` is optional.



5. **`routingtable`** section:

   .. _bootstrap_routingtable:

  The routing table section defines all the connections between the module
  queues therefor defining the event flow and order the events are passing
  through modules.

  The entries should have following format:

  ::

       source_module_instance_name.queue_name -> destination_module_instance_name.queue_name


  A sample extract:

  .. code-block:: yaml

        routingtable:
          - input.outbox            -> jsondecode.inbox
          - jsondecode.outbox       -> match.inbox
          - match.email             -> email.inbox
          - match.pagerduty         -> pagerduty.inbox
          - match.mattermost        -> mattermost.inbox
          - match.jira              -> jira.inbox
          - match.msteams           -> msteams.inbox


  * The routing table is obligatory
  * The routing table contains '->' indicating the relation between the
    source queue and the destination queue.


A complete example can be seen in the :ref:`examples <examples>` section.


.. _this schema: https://github.com/smetj/wishbone/blob/develop_3.0.0/wishbone/config/schema.py


