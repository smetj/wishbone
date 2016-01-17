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
    smetj/wishbone      latest              e4acd2360be8        40 minutes ago      932.3 MB
    smetj/wishbone      alertmachine        9bb81f6baa3a        4 months ago        756.2 MB

The container is prepared to be run as an executable:

.. code-block:: sh

    $ docker run -i -t smetj/wishbone:latest
    usage: wishbone [-h] {show,stop,list,start,kill,debug} ...
    wishbone: error: too few arguments


The following commands runs a Wishbone container:


.. code-block:: sh

    $ docker run --privileged=true -t -i --volume /bootstrap:/bootstrap smetj/wishbone:latest debug --config /bootstrap/simple.yaml

The idea is that the Docker *host* has a directory called "/bootstrap" which
contains all the Wishbone bootstrap files. The above command mounts the host's
**/bootstrap** directory to the container's mountpoint called "/bootstrap".
Once done you can point the *--config* parameter to the mountpoint and load
the bootstrap files stored on the host.

