.. _creating_a_module_function:
==========================
Creating a module function
==========================


Creating a module function is just a matter of creating a simple class.

In this example we will create a module function which calculates the grand
total of an itemized bill.

Some key points of a module function:

* Your class must base :py:class:`wishbone.function.module.ModuleFunction`
* Your class must have a ``do()`` method which accepts the event and returns it modified.
* Write a terse docstring as this will be used when issuing ``wishbone show --docs wishbone_external.function.module.grandtotal``.
* Install your template function along a similar entrypoint in ``setup.py``:
.. code-block:: python

  entry_points={
    'wishbone_external.module.grandtotal': [
        'grandtotal = wishbone_external.module.grantotal:GrandTotal'
    ]
  }

.. code-block:: python

    from wishbone.function.module import ModuleFunction


    class GrandTotal(ModuleFunction):
        '''
        Calculates the grand total of all articles.

        A Wishbone module function which calculates the grand total of all the
        article items stored under ``articles``.

        Args:
            source (str): The source field where the articles are stored
            destination (str): The destination field where to write the total.
        '''

        def __init__(self, source='data.articles', destination='data.total'):

            self.source = source
            self.destination = destination

        def do(self, event):
            '''
            The function mapped to the module function.

            Args:
                event (wishbone.event.Event): The Wishbone event.

            Returns:
                wishbone.event.Event: The modified event.
            '''

            total = 0
            for article, price in event.get(self.source).items():
                total += int(price)

            event.set(total, self.destination)
            return event


The following bootstrap YAML file demonstrates how the ``grandtotal`` module
can be used:

.. code-block:: YAML

    module_functions:
      make_grand_total:
        function: wishbone_external.function.module.grandtotal

    template_functions:
      get_price:
        function: wishbone.function.template.random_integer
        arguments:
          minimum: 1
          maximum: 100

    modules:
      input:
        module: wishbone.module.input.generator
        arguments:
          payload:
            articles:
              article_1: "{{ get_price() }}"
              article_2: "{{ get_price() }}"
              article_3: "{{ get_price() }}"
              article_4: "{{ get_price() }}"
              article_5: "{{ get_price() }}"

      output:
        module: wishbone.module.output.stdout
        functions:
          inbox:
            - make_grand_total
        arguments:
            selection: .

    routingtable:
      - input.outbox -> output.inbox


The output looks like:

.. code-block:: sh

    $ wishbone start --config module_function_grandtotal.yaml --no-fork
    Instance started in foreground with pid 29585
    2017-10-29T19:56:51.7004+00:00 wishbone[29585] debug input: Connected queue input._logs to _logs._input
    2017-10-29T19:56:51.7006+00:00 wishbone[29585] debug input: Connected queue input._metrics to _metrics._input
    2017-10-29T19:56:51.7007+00:00 wishbone[29585] debug input: Connected queue input.outbox to output.inbox
    2017-10-29T19:56:51.7009+00:00 wishbone[29585] debug input: preHook() found, executing
    2017-10-29T19:56:51.7010+00:00 wishbone[29585] debug input: Started with max queue size of 100 events and metrics interval of 10 seconds.
    2017-10-29T19:56:51.7011+00:00 wishbone[29585] debug output: Connected queue output._logs to _logs._output
    2017-10-29T19:56:51.7013+00:00 wishbone[29585] debug output: Connected queue output._metrics to _metrics._output
    2017-10-29T19:56:51.7014+00:00 wishbone[29585] debug output: preHook() found, executing
    2017-10-29T19:56:51.7015+00:00 wishbone[29585] debug output: Started with max queue size of 100 events and metrics interval of 10 seconds.
    2017-10-29T19:56:51.7016+00:00 wishbone[29585] debug output: Function 'consume' has been registered to consume queue 'inbox'
    {'cloned': False, 'bulk': False, 'data': {'articles': {'article_1': '39', 'article_2': '35', 'article_3': '64', 'article_4': '44', 'article_5': '71'}, 'total': 253}, 'errors': {}, 'tags': [], 'timestamp': 1509307012.7014496, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': 'b42ab53f-9f41-4ad4-814e-2c227537e4fe'}
    {'cloned': False, 'bulk': False, 'data': {'articles': {'article_1': '26', 'article_2': '95', 'article_3': '58', 'article_4': '10', 'article_5': '72'}, 'total': 261}, 'errors': {}, 'tags': [], 'timestamp': 1509307013.702464, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '94a854a6-8400-4a36-b790-070ee0bd5c2c'}
    {'cloned': False, 'bulk': False, 'data': {'articles': {'article_1': '36', 'article_2': '10', 'article_3': '96', 'article_4': '89', 'article_5': '82'}, 'total': 313}, 'errors': {}, 'tags': [], 'timestamp': 1509307014.7034726, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '020e5aed-50fd-46f9-a7a4-495b8a474984'}
