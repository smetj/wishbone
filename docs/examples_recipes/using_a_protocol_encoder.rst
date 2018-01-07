.. _using_a_protocol_encoder:

Using a protocol encoder
========================

.. code-block:: python

    from wishbone.actorconfig import ActorConfig
    from wishbone.router.default import Default
    from wishbone.componentmanager import ComponentManager


    def main():

        c = ComponentManager()
        protocol = c.getComponentByName("wishbone.protocol.encode.json")()

        router = Default()

        router.registerModule(
            module="wishbone.module.input.generator",
            actor_config=ActorConfig(
                name='input',
            ),
            arguments={
                "payload": {"one": 1, "two": 2}
            }
        )

        router.registerModule(
            module="wishbone.module.output.stdout",
            actor_config=ActorConfig(
                name='output',
                protocol=protocol
            ),
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
        protocol: wishbone.protocol.encode.json

    modules:
      input:
        module: wishbone.module.input.generator
        arguments:
          payload:
            one: 1
            two: 2

      output:
        module: wishbone.module.output.stdout
        protocol: json

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
    {"one": 1, "two": 2}
    {"one": 1, "two": 2}
    {"one": 1, "two": 2}
    {"one": 1, "two": 2}

