.. _using_a_module_function:

Using a module function
=======================

This example explains how to use a module function adding a tag the events
passing through.


**Coded in Python**

.. code-block:: python

    from wishbone.actorconfig import ActorConfig
    from wishbone.router.default import Default
    from wishbone.componentmanager import ComponentManager


    def main():

        router = Default()

        f = ComponentManager().getComponentByName("wishbone.function.module.append")
        f_instance = f(
            data="you_are_tagged",
            destination="tags"
        )

        router.registerModule(
            module="wishbone.module.input.generator",
            actor_config=ActorConfig(
                name='input'
            )
        )

        router.registerModule(
            module="wishbone.module.output.stdout",
            actor_config=ActorConfig(
                name='output',
                module_functions={
                    "inbox": [
                        f_instance
                    ]
                }
            ),
            arguments={
                "selection": "."
            }
        )

        router.connectQueue('input.outbox', 'output.inbox')
        router.start()
        router.block()


    if __name__ == '__main__':
        main()


**Bootstrap File**

The following bootstrap file does exactly the same as the above ``python`` version:

.. code-block:: YAML

    ---
    module_functions:
      tagit:
        function: wishbone.function.module.append
        arguments:
            data: you_are_tagged
            destination: tag

    modules:
      input:
        module: wishbone.module.input.generator

      output:
        module: wishbone.module.output.stdout
        module_functions:
            - tagit
        arguments:
            selection: .

    routingtable:
      - input.outbox -> output.inbox
    ...


**Server output**:

The server can be started on CLI using the ``wishbone`` executable:

.. code-block:: sh

    $ wishbone start --config boostrap.yaml --nofork
    Instance started in foreground with pid 16695
    2017-10-29T17:40:30.1223+00:00 wishbone[16695] debug input: Connected queue input._logs to _logs._input
    2017-10-29T17:40:30.1224+00:00 wishbone[16695] debug input: Connected queue input._metrics to _metrics._input
    2017-10-29T17:40:30.1226+00:00 wishbone[16695] debug input: Connected queue input.outbox to output.inbox
    2017-10-29T17:40:30.1227+00:00 wishbone[16695] debug input: preHook() found, executing
    2017-10-29T17:40:30.1229+00:00 wishbone[16695] debug input: Started with max queue size of 100 events and metrics interval of 10 seconds.
    2017-10-29T17:40:30.1230+00:00 wishbone[16695] debug output: Connected queue output._logs to _logs._output
    2017-10-29T17:40:30.1231+00:00 wishbone[16695] debug output: Connected queue output._metrics to _metrics._output
    2017-10-29T17:40:30.1232+00:00 wishbone[16695] debug output: preHook() found, executing
    2017-10-29T17:40:30.1234+00:00 wishbone[16695] debug output: Started with max queue size of 100 events and metrics interval of 10 seconds.
    2017-10-29T17:40:30.1235+00:00 wishbone[16695] debug output: Function 'consume' has been registered to consume queue 'inbox'
    {'cloned': False, 'bulk': False, 'data': 'test', 'errors': {}, 'tags': ['you_are_tagged'], 'timestamp': 1509298831.1225557, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '8d1489f7-7d55-4a26-8114-69c68c7b5ecf'}
    {'cloned': False, 'bulk': False, 'data': 'test', 'errors': {}, 'tags': ['you_are_tagged'], 'timestamp': 1509298832.124007, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '854f31a4-cf96-446e-9712-a4e3d5a8b38b'}
    {'cloned': False, 'bulk': False, 'data': 'test', 'errors': {}, 'tags': ['you_are_tagged'], 'timestamp': 1509298833.1251073, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '76fec0c3-0690-4683-90aa-ae5d7c5b6b34'}
    {'cloned': False, 'bulk': False, 'data': 'test', 'errors': {}, 'tags': ['you_are_tagged'], 'timestamp': 1509298834.1261678, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': 'a50af14d-cc7c-4449-864b-92a86d727de0'}
    {'cloned': False, 'bulk': False, 'data': 'test', 'errors': {}, 'tags': ['you_are_tagged'], 'timestamp': 1509298835.1271603, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '4bcfba25-e700-484f-8fee-73ac77597e3f'}
    {'cloned': False, 'bulk': False, 'data': 'test', 'errors': {}, 'tags': ['you_are_tagged'], 'timestamp': 1509298836.1281745, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '5cb0f80e-742a-47fa-a971-f10744467358'}


