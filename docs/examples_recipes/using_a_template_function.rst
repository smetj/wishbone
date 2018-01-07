Using a template function
=========================
.. _using_a_template_function:

This example explains how to use a template function to feed module parameters
a `dynamic` value.  In this example we initialize
``wishbone.function.template.choice`` by setting its
:paramref:`wishbone.function.template.choice.Choice.array` parameter.

**Coded in Python**

.. code-block:: python
    :emphasize-lines: 10,11,17-19,22

    from wishbone.actorconfig import ActorConfig
    from wishbone.router.default import Default
    from wishbone.componentmanager import ComponentManager


    def main():

        router = Default()

        f = ComponentManager().getComponentByName("wishbone.function.template.choice")
        f_instance = f(["one", "two", "three"])

        router.registerModule(
            module="wishbone.module.input.generator",
            actor_config=ActorConfig(
                name='input',
                template_functions={
                    "gimmeNumber": f_instance
                }
            ),
            arguments={
                "payload": "The value '{{gimmeNumber()}}' is chosen."
            }
        )

        router.registerModule(
            module="wishbone.module.output.stdout",
            actor_config=ActorConfig(
                name='output'
            )
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
    template_functions:
      gimmeNumber:
        function: wishbone.function.template.choice
        arguments:
          array:
            - one
            - two
            - three

    modules:
      input:
        module: wishbone.module.input.generator
        arguments:
          payload: The value '{{gimmeNumber()}}' is chosen.

      output:
        module: wishbone.module.output.stdout

    routingtable:
      - input.outbox -> output.inbox
    ...


**Server output**:

The server can be started on CLI using the ``wishbone`` executable:

.. code-block:: sh

    $ wishbone start --config boostrap.yaml --nofork
    Instance started in foreground with pid 32206
    2017-10-27T10:58:57.6725+00:00 wishbone[32206] debug input: Connected queue input._logs to _logs._input
    2017-10-27T10:58:57.6727+00:00 wishbone[32206] debug input: Connected queue input._metrics to _metrics._input
    2017-10-27T10:58:57.6728+00:00 wishbone[32206] debug input: Connected queue input.outbox to output.inbox
    2017-10-27T10:58:57.6729+00:00 wishbone[32206] debug input: preHook() found, executing
    2017-10-27T10:58:57.6731+00:00 wishbone[32206] debug input: Started with max queue size of 100 events and metrics interval of 10 seconds.
    2017-10-27T10:58:57.6732+00:00 wishbone[32206] debug output: Connected queue output._logs to _logs._output
    2017-10-27T10:58:57.6733+00:00 wishbone[32206] debug output: Connected queue output._metrics to _metrics._output
    2017-10-27T10:58:57.6734+00:00 wishbone[32206] debug output: preHook() found, executing
    2017-10-27T10:58:57.6736+00:00 wishbone[32206] debug output: Started with max queue size of 100 events and metrics interval of 10 seconds.
    2017-10-27T10:58:57.6737+00:00 wishbone[32206] debug output: Function 'consume' has been registered to consume queue 'inbox'
    The value 'one' is chosen.
    The value 'three' is chosen.
    The value 'three' is chosen.
    The value 'two' is chosen.
