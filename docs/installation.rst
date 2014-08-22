============
Installation
============

Wishbone works on python 2.7+ and PyPy 2.3.1+

Versioning
----------

- Wishbone uses `Semantic Versioning`_.
- Each release is tagged in `Github`_ with the release number.
- The master branch contains the latest stable release.
- The development branch is where all development is done.


Wishbone
--------

Pypi
'''''

To install the latest stable release from
https://pypi.python.org/pypi/wishbone use *pip*.

.. code-block:: sh

    $ pip install wishbone




From source
'''''''''''
Wishbone' source can be downloaded from http://github.com/smetj/wishbone


Stable
~~~~~~

Install the latest *stable* release from the **master** branch.

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone
    $ cd wishbone
    $ cd checkout master #just in case your repo is in another branch
    $ sudo python setup.py install


Development
~~~~~~~~~~~

Install the latest *development* release from the **development** branch.

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone.git
    $ cd wishbone
    $ git checkout develop
    $ sudo python setup.py install


Docker
''''''

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

    $ docker run --privileged=true -t -i --volume /bootstrap:/bootstrap smetj/wishbone:1.0.0 debug --config /bootstrap/simple.yaml

The idea is that the Docker *host* has a directory called "/bootstrap" which
contains all the Wishbone bootstrap files. The above command mounts the host's
**/bootstrap** directory to the container's mountpoint called "/bootstrap".
Once done you can point the *--config* parameter to the mountpoint and load
the bootstrap files stored on the host.



Verify installation
'''''''''''''''''''

Once installed you should have the `wishbone` executable available in your search
path:

.. code-block:: sh

    $ wishbone --help
    usage: wishbone [-h] {start,debug,stop,kill,list,show} ...

    Wishbone bootstrap server.

    positional arguments:
      {start,debug,stop,kill,list,show}

    optional arguments:
      -h, --help            show this help message and exit

.. _semantic versioning: http://semver.org/
.. _Github: https://github.com/smetj/wishbone/releases