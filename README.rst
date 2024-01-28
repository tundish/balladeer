Overview
::::::::

Balladeer_ is a Python package for creating web-enabled interactive screenplay.

For tutorials and updates, please visit the `development blog`_ site.

An API manual is included in the `code repository`_ and is available to `read online`_.

Installation
============

Here are the install instructions for Linux. You need Python version 3.11 or higher.

Virtual Environment
-------------------

#. First make a fresh Python virtual environment::

    python3 -m venv ~/ballad

Packages
--------

#. Update the package manager within it::

    ~/ballad/bin/python -m pip install -U pip wheel

#. Install (or update) Balladeer::

    ~/ballad/bin/python -m pip install -U balladeer

Examples
========

#. Download the `repository as a zip file <https://github.com/tundish/balladeer/archive/master.zip>`_.
   Unzip it to a local directory.

#. `cd` to one of the directories under `examples`::

    cd balladeer/examples/ex_00_hello_world

#. Run the example like this::

    ~/ballad/bin/python -m main

    Hello, World!

.. _balladeer: https://pypi.org/project/balladeer/
.. _code repository: https://github.com/tundish/balladeer
.. _development blog: https://tundish.github.io/balladeer/
.. _read online: https://balladeer.readthedocs.io/en/latest/index.html
