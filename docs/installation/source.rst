======
Source
======

Wishbone source can be downloaded from http://github.com/smetj/wishbone


Prerequisites:
--------------

- automake >=1.11.2
- Typical build tools like configure, make, gcc ...


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
