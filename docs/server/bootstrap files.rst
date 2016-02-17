===============
Bootstrap Files
===============

Bootstrap files are YAML formatted configuration files used to start a
Wishbone server on command line.

A bootstrap file contains the configuration of all the lookup functions and
modules to initialize and how they are connected to each other.

Bootstrap files are loaded using the *--config* option:

.. code::

    $ wishbone start --config static_dynamic.yaml

**Example bootstrap file**

.. literalinclude:: ../static/static_dynamic.yaml
   :language: yaml
   :linenos:


Bootstrap files consist out of 3 sections:

lookups
-------

See `lookup functions`_ for more information.

The *lookups* section has following format in JSON-schema:

.. code-block:: json

    {
      "lookups": {
        "patternProperties": {
          ".*": {
            "additionalProperties": false,
            "properties": {
              "arguments": {
                "type": "object"
              },
              "module": {
                "type": "string"
              }
            },
            "required": [
              "module"
            ],
            "type": "object"
          }
        },
        "type": "object"
      }
    }

The name of the key (line 3) defines the name of the function to use in the
*module section* (line 11).

**Parameters**:

**module**

The name of the module to load in dotted format.

If the lookup name is *wishbone.lookup.randomword* then the following Ptyhon
code should be able to execute successfully:

.. code-block:: python

  from wishbone.lookup import randomword

**arguments**

An optional dictionary of arguments used to initialize the lookup module.


modules
-------

The *modules* section has following format in JSON-schema:

.. code-block:: json

    {
      "patternProperties": {
        ".*": {
          "additionalProperties": false,
          "properties": {
            "arguments": {
              "type": "object"
            },
            "description": {
              "type": "string"
            },
            "module": {
              "type": "string"
            }
          },
          "required": [
            "module"
          ],
          "type": "object"
        }
      },
      "type": "object"
    }

The name of the key (line 7) defines the name of the module instance.

**Parameters**:

**description**

An optional description explaining what the module does.
The descriptoin appears in the module and queue graph.
See --monitor option.

**arguments**

An optional dictionary of keyword arguments used to initialize the module.


routingtable
------------

The *routing* section has following format in JSON-schema:

.. code-block:: json

    {
      "routingtable": {
        "type": "array"
      }
    }

The routing table connects the queues of the different module instances into
the desired flow.

The section consists out of a list of entries containing a source
queue, a separator -> and a destination queue.

A queue can only be connected to 1 single queue.

.. warning::

  If you need to have *"one to many"* or *"many to one"* connections then you
  can use the  :py:class:`wishbone.module.Fanout` and
  :py:class:`wishbone.module.Fanout` modules.


.. _UpLook: https://github.com/smetj/uplook
.. _lookup functions: ../server/lookup%20functions.html
