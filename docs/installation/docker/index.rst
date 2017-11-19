:tocdepth: 1

======
Docker
======

.. NOTE::

    The foreseen containers are big.  I know they can be made much smaller but
    the time I can spend on this is limited thus any help would be much
    appreciated.


Wishbone is also available as a Docker container.

Pull the *smetj/wishbone* repository from
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
- The ``develop`` tag tracks the Wishbone develop_ branch.
- The ``master`` tag tracks the Wishbone master_ branch.


The container entrypoint is pointing to the wishbone executable:

.. code-block:: sh

    $ docker run -t -i smetj/wishbone:develop
    usage: wishbone [-h] {start,stop,list,show} ...
    wishbone: error: the following arguments are required: command



The following commands runs a Wishbone container:


.. code-block:: sh

    $ docker run --volume ${PWD}/bootstrap.yaml:/tmp/bootstrap.yaml smetj/wishbone:2.1.0 debug --config /tmp/bootstrap.yaml

The default containers don't contain bootstrap files.  The idea is that you
have to mount the bootstrap file into the container and refer to it using the
**--config** argument.


Docker build file
~~~~~~~~~~~~~~~~~

This example build file creates a Wishbone Docker container:

.. code-block:: sh

    FROM            centos:centos7
    MAINTAINER      Jelle Smet
    EXPOSE          19283
    RUN             yum install -y wget automake autoconf make file libtool gcc  gcc-c++ python-dev bzip2
    RUN             wget -qO- https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-4.0.1-linux_x86_64-portable.tar.bz2|tar xjv -C /opt
    RUN             wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
    RUN             /opt/pypy-4.0.1-linux_x86_64-portable/bin/pypy /tmp/get-pip.py
    RUN             /opt/pypy-4.0.1-linux_x86_64-portable/bin/pip install cython
    RUN             /opt/pypy-4.0.1-linux_x86_64-portable/bin/pip install --process-dependency-link https://github.com/smetj/wishbone/archive/develop.zip
    ENTRYPOINT      ["/opt/pypy-4.0.1-linux_x86_64-portable/bin/wishbone"]


.. toctree::
    extending_wishbone_containers

.. here: https://github.com/smetj/wishbone_docker
.. develop: https://github.com/smetj/wishbone/tree/develop
.. develop: https://github.com/smetj/wishbone
