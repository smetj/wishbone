:tocdepth: 1

======
Docker
======

.. NOTE::

    The Wishbone containers are big.  Any help reducing the size is highly appreciated.


Pull the ``smetj/wishbone`` repository from
https://registry.hub.docker.com/u/smetj/wishbone into your Docker environment:

The docker files necessary to build Wishbone containers can be found here_.

.. code-block:: sh

    $ docker pull smetj/wishbone
    $ docker images
    REPOSITORY                                            TAG                 IMAGE ID            CREATED              SIZE
    smetj/wishbone                                        base_python         72c6cc524d53        26 minutes ago       778 MB
    smetj/wishbone                                        develop             81e425eb6784        5 minutes ago       806 MB


- The ``smetj/wishbone:base_python`` container is a Python3.6 based container
  containing the necessary dependencies to install Wishbone.
- The ``develop`` tag tracks the Wishbone `develop`_ branch.
- The ``master`` tag tracks the Wishbone `master`_ branch.


The container entrypoint is pointing to the wishbone executable:

.. code-block:: sh

    $ docker run -t -i smetj/wishbone:develop
    usage: wishbone [-h] {start,stop,list,show} ...
    wishbone: error: the following arguments are required: command



The following commands runs a Wishbone container:


.. code-block:: sh

    $ docker run --volume ${PWD}/bootstrap.yaml:/tmp/bootstrap.yaml smetj/wishbone:develop start --config /tmp/bootstrap.yaml


Installing additional modules
-----------------------------

To install additional Wishbone modules inside the Docker container you will have to build a new container.

.. code-block:: text

    FROM            smetj/wishbone:develop
    MAINTAINER      Jelle Smet
    RUN             /opt/python/bin/pip3 install --process-dependency-link https://github.com/smetj/wishbone-input-httpserver/archive/wishbone3.zip

Building the container:

.. code-block:: sh

    $ docker run -t -i smetj/wishbone:http list

Running the container:

.. code-block:: sh

    $ docker run -t -i smetj/wishbone:http list
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 3.0.0

    +------------------+----------------+----------+----------------+---------+-------------------------------------------------------------------------+
    | Namespace        | Component type | Category | Name           | Version | Description                                                             |
    +------------------+----------------+----------+----------------+---------+-------------------------------------------------------------------------+
    |                  |                |          |                |         |                                                                         |
    | wishbone         | protocol       | decode   | dummy          |   3.0.0 | A dummy decoder.                                                        |
    |                  |                |          | json           |   3.0.0 | Decode JSON data into a Python data structure.                          |
    |                  |                |          | msgpack        |   3.0.0 | Decode MSGpack data into a Python data structure.                       |
    |                  |                |          | plain          |   3.0.0 | Decode plaintext using the defined charset.                             |
    |                  |                |          |                |         |                                                                         |
    |                  |                | encode   | dummy          |   3.0.0 | A dummy encoder.                                                        |
    |                  |                |          | json           |   3.0.0 | Encode data into JSON format.                                           |
    |                  |                |          | msgpack        |   3.0.0 | Encode data into msgpack format.                                        |
    |                  |                |          |                |         |                                                                         |

    ...snip ...

    | wishbone_contrib | module         | input    | httpserver     |   1.1.0 | Receive events over HTTP.                                               |
    |                  |                |          |                |         |                                                                         |
    +------------------+----------------+----------+----------------+---------+-------------------------------------------------------------------------+


.. here: https://github.com/smetj/wishbone_docker
.. develop: https://github.com/smetj/wishbone/tree/develop
.. master: https://github.com/smetj/wishbone
