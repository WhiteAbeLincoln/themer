XThemer
======
Configures a global theme for X, using the `base16`_ format.

.. _base16: https://github.com/chriskempson/base16

BUILDING
--------
- Install python3
- Setup virtualenv with :code:`python3 -m venv .env`
- Start virtualenv with :code:`source .env/bin/activate`
- Install packages with :code:`pip install -r requirements.txt`

RUNNING
-------
- Run script with :code:`xthemer <theme>`

INSTALLATION
------------
Install with :code:`pip install xthemer` or :code:`cd themer && pip install .`
Currently installing has issues with wheel distributions, since the template files don't
get copied to the correct directories. Therefore it is recommended to install from source
until this bug gets worked out

ATTRIBUTION
-----------
Templates are for the most part from the base16 project, and are copyright of their respective authors
