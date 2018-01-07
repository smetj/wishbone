===========================
Passing variables to Docker
===========================

:py:class:`wishbone.function.template.environment <wishbone.function.template.environment.Environment>`
is a template function to access and use environment variables in your
bootstrap file. When using the ``wishbone`` executable then the ``env()``
template function is loaded automatically.

This might be practical when using the containerized version of Wishbone.

Consider following bootstrap file:

.. code-block:: yaml

    modules:
      input:
        module: wishbone.module.input.generator
        arguments:
          payload: '{{env("message")}}'

      output:
        module: wishbone.module.output.stdout

    routingtable:
      - input.outbox -> output.inbox

We can bootstrap a Wishbone container using following command:

.. code-block:: sh

    $ docker run -t -i --env message="hello world" -v $(pwd)/hello_world.yaml:/tmp/bootstrap.yaml docker.io/smetj/wishbone:develop start --config /tmp/bootstrap.yaml
    Instance started in foreground with pid 1
    {'cloned': False, 'bulk': False, 'data': 'hello world', 'errors': {}, 'tags': [], 'timestamp': 1511299095.2465549, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '2e6f6a44-50ef-4517-a727-0f3e0af0e6ab'}
    {'cloned': False, 'bulk': False, 'data': 'hello world', 'errors': {}, 'tags': [], 'timestamp': 1511299096.2474735, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '5c18eb80-5529-4f01-aa33-8f7286bc4769'}
    {'cloned': False, 'bulk': False, 'data': 'hello world', 'errors': {}, 'tags': [], 'timestamp': 1511299097.2487144, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '39edee41-bba1-4b81-9251-98b411f09918'}
    {'cloned': False, 'bulk': False, 'data': 'hello world', 'errors': {}, 'tags': [], 'timestamp': 1511299098.2498908, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '52f9709f-de1d-467d-8f53-f9c311e2bcc9'}
    {'cloned': False, 'bulk': False, 'data': 'hello world', 'errors': {}, 'tags': [], 'timestamp': 1511299099.2510643, 'tmp': {}, 'ttl': 253, 'uuid_previous': [], 'uuid': '9443e1d0-dddc-41a8-bd8c-be291881876c'}


