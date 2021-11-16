Balladeer
:::::::::

This is a Python package for creating web-enabled interactive screenplay.
For documentation, please visit the `development blog site
<https://tundish.github.io/balladeer/>`_.

Installation
============

Here are the install instructions for Linux. You need Python version 3.8 or higher.

Virtual Environment
-------------------

#. First make a fresh Python virtual environment::

    python3 -m venv ~/balladeer-app

Packages
--------

#. Update the package manager within it::

    ~/balladeer-app/bin/pip install -U pip wheel

#. Install (or update) Balladeer::

    ~/balladeer-app/bin/pip install -U balladeer

Examples
========

Downloads and Dependencies
--------------------------

#. Install dependencies::

    ~/balladeer-app/bin/pip install aiohttp

#. Download the `repository as a zip file <https://github.com/tundish/balladeer/archive/master.zip>`_.
   Unzip it to a local directory.

Operation
---------

#. `cd` to one of the directories under `examples`::

    cd examples/00_hello_world

#. Run the example like this::

    ~/balladeer-app/bin/python hello.py

    Hello, World!

