.. image:: pics/ascii.png

.. image:: pics/GitHub-Mark-64px.png
    :align: right
    :target: https://github.com/smetj/wishbone

**A pragmatists framework to build reactive event processing services.**

.. warning::
   This documentation is still WIP

What?
-----

Wishbone is a **Python** framework to build reactive event processing
services by combining and connecting modules into a :ref:`processing pipeline
<processing pipeline>` through which :ref:`events <events>` flow, modify and
trigger interactions with remote services.

The framework can be used to implement a wide area of solutions such as
`mashup enablers`_, `ETL servers`_, `stream processing servers`_, `webhook
services`_ , `ChatOps services`_, bots and all kinds of event driven
automation.

.. image:: pics/separator_2.png
    :align: center
    :scale: 75%

Why?
----

The goal of the project is to provide an expressive and ops friendly framework
which removes a maximum of boilerplate related to:

* including custom code
* plugin management
* CLI process management
* error handling
* logging
* metrics
* instance configuration files

.. image:: pics/separator_2.png
    :align: center
    :scale: 75%

When?
-----

Wishbone is probably going to be helpful to you when you need to tackle the:

    "`If this happens I want that to happen ...`" - kind of problems.

|


.. image:: pics/separator_2.png
    :align: center
    :scale: 75%


.. toctree::
    :hidden:
    :maxdepth: 3

    installation/index
    components/index
    bootstrap_cli/index
    python/index
    examples_recipes/index

.. _mashup enablers: https://en.wikipedia.org/wiki/Mashup_(web_application_hybrid)#Mashup_enabler
.. _ETL servers: https://en.wikipedia.org/wiki/Extract,_transform,_load
.. _stream processing servers: https://en.wikipedia.org/wiki/Stream_processing
.. _CEP: https://en.wikipedia.org/wiki/Complex_event_processing
.. _ChatOps services: https://www.google.com/search?newwindow=1&q=chatops
.. _webhook services: https://en.wikipedia.org/wiki/Webhook
