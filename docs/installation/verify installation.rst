===================
Verify installation
===================

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


Execute tests
~~~~~~~~~~~~~

.. code-block:: sh

    $ python setup.py test