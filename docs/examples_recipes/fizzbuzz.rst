=====================
HTTP Fizzbuzz Example
=====================

This `example` Wishbone server accepts `JSON` data over http on the ``/colors``
endpoint and replies to the client with the defined ``response`` for it. The
``categorize`` module instance validates whether the value of ``color`` is
either `red, green or blue` and forwards the event to the ``requestbin``
module instance if so. If not, the complete event is printed to STDOUT. The
``requestbin`` module submits the event to the defined ``url`` extended by the
`requestbin_id` value defined by the user.  After submitting the event
successfully to the defined ``url``, the complete event is printed to STDOUT.

Depending on the modules chosen you

Server
------

.. code-block:: bash

    $ wishbone start --config fizzbuzz.yaml --nofork
    Instance started in foreground with pid 25260
    ... snip ...
    2017-09-30T14:18:46.7928+00:00 wishbone[25260] informational input: Serving on 0.0.0.0:19283 with a connection poolsize of 1000.

Bootstrap file
--------------

.. code-block:: yaml

  ---
  protocols:
    json_decode:
      protocol: wishbone.protocol.decode.json
    json_encode:
      protocol: wishbone.protocol.encode.json

  modules:
    input:
      module: wishbone_contrib.module.input.httpserver
      protocol: json_decode
      arguments:
        resource:
          colors:
            users: []
            tokens: []
            response: Hi '{{tmp.input.env.http_user_agent}}' on '{{tmp.input.env.remote_addr}}'. Your id is '{{uuid}}'. Thank you for choosing Wishbone ;)'

    categorize:
      module: wishbone.module.flow.queueselect
      arguments:
        templates:
          - name: primary
            queue: >
              {{ 'primary' if data.color in ("red", "green", "blue") else 'not_primary' }}
            payload:
              greeting: Hello
              message: '{{data.color}} is an awesome choice'

    funnel:
      module: wishbone.module.flow.funnel

    requestbin:
      protocol: json_encode
      module: wishbone.module.output.http
      arguments:
        method: PUT
        url: 'https://requestb.in/{{data.requestbin_id}}'
        selection: tmp.categorize.payload

    stdout:
      module: wishbone.module.output.stdout
      protocol: json_encode
      arguments:
        selection: .

  routingtable:
    - input.colors           -> categorize.inbox

    - categorize.primary     -> requestbin.inbox
    - categorize.not_primary -> funnel.not_primary

    - requestbin.success     -> funnel.requestbin

    - funnel.outbox          -> stdout.inbox
  ...


Client
------

.. code-block:: bash

    $ curl -d '{"color":"red", "requestbin_id": "abcdefg"}' http://localhost:19283/colors
    Hi 'curl/7.53.1' on '127.0.0.1'. Your id is 'd805df4c-816e-4af2-bb32-8454cae366aa'.


Server STDOUT after submitting event
------------------------------------

.. code-block:: json

  {
    "cloned": true,
    "bulk": false,
    "data": {
      "color": "red",
      "requestbin_id": "abcdefg"
    },
    "errors": {},
    "tags": [],
    "timestamp": 1506791239.4684186,
    "tmp": {
      "input": {
        "remote_addr": "127.0.0.1",
        "request_method": "POST",
        "user_agent": "curl/7.53.1",
        "queue": "colors",
        "username": "",
        "response": "Hi 'curl/7.53.1' on '127.0.0.1'. Your id is 'd805df4c-816e-4af2-bb32-8454cae366aa'. Thank you for choosing Wishbone ;)"
      },
      "categorize": {
        "original_event_id": "94ff6c3b-3c83-41c5-b5b7-091f244e85a5",
        "queue": "primary",
        "payload": {
          "greeting": "Hello",
          "message": "red is an awesome choice"
        }
      },
      "requestbin": {
        "server_response": "ok",
        "status_code": 200,
        "url": "https://requestb.in/abcdefg",
        "method": "PUT",
        "useragent": "wishbone.module.output.http/3.0.0"
      }
    },
    "ttl": 251,
    "uuid_previous": [
      "94ff6c3b-3c83-41c5-b5b7-091f244e85a5"
    ],
    "uuid": "d805df4c-816e-4af2-bb32-8454cae366aa"
  }
