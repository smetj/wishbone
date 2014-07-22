============
Installation
============


Wishbone
--------

Pypi
'''''

You can install the latest stable version of Wishbone from
https://pypi.python.org/pypi/wishbone/ by using pip:

.. code-block:: sh

    $ pip install wishbone

All dependencies should be resolved automatically.


From source
'''''''''''

You can install the latest stable or development version from
https://github.com/smetj/wishbone

Stable
~~~~~~

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone
    $ cd wishbone
    $ cd checkout master #just in case your repo is in another branch
    $ sudo python setup.py install


Development
~~~~~~~~~~~

To install the latest development release you have to checkout the develop
branch and build from there:

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone.git
    $ cd wishbone
    $ git checkout develop
    $ sudo python setup.py install


Docker
''''''

As of version 0.5 a Docker container of Wishbone is available.
TODO(smetj): more info


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
