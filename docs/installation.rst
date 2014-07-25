============
Installation
============

Wishbone works on python 2.7+ and PyPy 2.3.1+

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
