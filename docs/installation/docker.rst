======
Docker
======

Wishbone is also available as a Docker container.

Pull the *smetj/wishbone* repository from
https://registry.hub.docker.com/u/smetj/wishbone into your Docker environment:

.. code-block:: sh

    $ docker pull smetj/wishbone
    $ docker images
    REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
    smetj/wishbone      development         e4acd2360be8        40 minutes ago      932.3 MB
    smetj/wishbone      2.1.0               9bb81f6baa3a        4 months ago        756.2 MB


The container entrypoint is pointing to the wishbone executable:

.. code-block:: sh

    $ docker run -i -t smetj/wishbone:latest
    usage: wishbone [-h] {show,stop,list,start,kill,debug} ...
    wishbone: error: too few arguments


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
