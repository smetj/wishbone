======
Source
======

.. NOTE::

    You really should install Wishbone inside `virtualenv`_ so you do not mess with
    your OS Python packages.

Wishbone source can be downloaded from http://github.com/smetj/wishbone

CI builds can be seen here: https://travis-ci.org/smetj/wishbone


**Stable**

Install the latest *stable* release from the **master** branch.

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone
    $ cd wishbone
    $ cd checkout master #just in case your repo is in another branch
    $ sudo python setup.py install


**Development**

Install the latest *development* release from the **development** branch.

.. code-block:: sh

    $ git clone https://github.com/smetj/wishbone.git
    $ cd wishbone
    $ git checkout develop
    $ sudo python setup.py install


**Execute tests**

.. code-block:: sh

    $ python setup.py test


.. _virtualenv: https://virtualenv.pypa.io/en/stable/
