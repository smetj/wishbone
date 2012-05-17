==============
 Installation
==============

Python Versions
===============

cliff is being developed under Python 2.7

.. _install-basic:

Basic Installation
==================

Wishbone should be installed into the same site-packages area where the
application and extensions are installed (either a virtualenv or the
global site-packages). You may need administrative privileges to do
that.  

Wishbone is build upon the latest features available in gevent (http://www.gevent.org).
So installing Wishbone consists out of 2 steps:

* Download and install a recent gevent.
* Download and install Wishbone.

------
Gevent
------

Download and install the latest gevent from https://bitbucket.org/denis/gevent/downloads

The steps to take typically involve something like:

.. code-block:: bash

   $ wget https://bitbucket.org/denis/gevent/get/1.0b2.tar.gz
   $ tar -xvzf 1.0b2.tar.gz
   $ cd [into_directory]
   $ sudo python setup.py install

.. note::

   If gevent fails to install check whether you have installed following package and its dependencies:

.. code-block:: bash

   $ aptitude show libevent-dev
   
   Package: libevent-dev                    
   State: installed
   Automatically installed: no
   Version: 2.0.16-stable-1
   Priority: optional
   Section: libdevel
   Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
   Architecture: amd64
   Uncompressed Size: 1,353 k
   Depends: libevent-2.0-5 (= 2.0.16-stable-1), libevent-core-2.0-5 (= 2.0.16-stable-1), libevent-extra-2.0-5 (= 2.0.16-stable-1), libevent-pthreads-2.0-5 (= 2.0.16-stable-1),
            libevent-openssl-2.0-5 (= 2.0.16-stable-1)
   Conflicts: libevent-dev
   Description: Asynchronous event notification library (development files)
    Libevent is an asynchronous event notification library that provides a mechanism to execute a callback function when a specific event occurs on a file descriptor or after a
    timeout has been reached. 
    
    This package includes development files for compiling against libevent.
   Homepage: http://www.monkey.org/~provos/libevent/

   Make sure you have the latest gevent build installed by downloading and
   installing gevent from https://bitbucket.org/denis/gevent/wiki/Home::
      $ hg clone https://bitbucket.org/denis/gevent

--------
Wishbone
--------

Download and install the latest wishbone from https://github.com/smetj/wishbone/tarball/master

The steps to take typically involve something like:

.. code-block:: bash

   $ wget https://github.com/smetj/wishbone/tarball/master -O wishbone.tar.gz
   $ tar -xvzf wishbone.tar.gz
   $ cd [into_directory]
   $ sudo python setup.py install


Source Code
===========

The source is hosted on github: https://github.com/smetj/wishbone

Reporting Bugs
==============

Please report bugs through the github project:
https://github.com/smetj/wishbone/issues

