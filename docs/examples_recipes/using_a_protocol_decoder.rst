.. _using_a_protocol_decoder:

Using a protocol decoder
========================

.. code-block:: python

    from wishbone.actorconfig import ActorConfig
    from wishbone.router.default import Default
    from wishbone.componentmanager import ComponentManager


    def main():

        c = ComponentManager()
        protocol = c.getComponentByName("wishbone.protocol.decode.json")()

        router = Default()

        router.registerModule(
            module="wishbone.module.input.generator",
            actor_config=ActorConfig(
                name='input',
                protocol=protocol
            ),
            arguments={
                "payload": '{"one": 1}'
            }
        )

        router.registerModule(
            module="wishbone.module.output.stdout",
            actor_config=ActorConfig(
                name='output',
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


The equivalent using a bootstrap file:

.. code-block:: yaml

    protocols:
      json:
        protocol: wishbone.protocol.decode.json

    modules:
      input:
        module: wishbone.module.input.generator
        protocol: json
        arguments:
          payload: '{"one": 1}'

      output:
        module: wishbone.module.output.stdout
        arguments:
          selection: .

    routingtable:
      - input.outbox -> output.inbox


The output:

.. code-block:: sh

    $ wishbone start --config demo_decode.yaml --nofork

    Instance started in foreground with pid 8899
    2017-11-01T13:16:59.6693+00:00 wishbone[8899] debug _logs: Connected queue _logs._logs to _logs.__logs
    2017-11-01T13:16:59.6695+00:00 wishbone[8899] debug _logs: Connected queue _logs._metrics to _metrics.__logs
    2017-11-01T13:16:59.6697+00:00 wishbone[8899] debug _logs: Module instance '_logs' has no queue '__metrics' so auto created.
    2017-11-01T13:16:59.6698+00:00 wishbone[8899] debug _logs: Module instance '_logs' has no queue '_input' so auto created.
    2017-11-01T13:16:59.6699+00:00 wishbone[8899] debug _logs: Module instance '_logs' has no queue '_output' so auto created.
    ... snip ...
    {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1509542220.6696804, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '4e754cec-402f-48b6-8a25-af3afeeb65fb'}
    {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1509542221.670773, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '7cc500bc-750f-476a-b7b3-4d1adb522218'}
    {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1509542222.6718802, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': 'ede9fc76-f5d7-4102-95ac-c7a3aacebfd7'}
    {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1509542223.672989, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '06291f44-10ba-4194-8e9b-4e6817fae5d2'}
    {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1509542224.6740425, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '294d24c7-e713-4e8b-be88-c14322917e96'}
    {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1509542225.6750607, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '8493d02a-2f55-468e-900c-a5286e842f7a'}
    {'cloned': False, 'bulk': False, 'data': {'one': 1}, 'errors': {}, 'tags': [], 'timestamp': 1509542226.6760375, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '369eebe5-2bb1-4c71-ba73-c3be78915db2'}

