===============
ts_Electrometer
===============
A CSC for the Electrometer.
Released as needed.

Dependencies
============

.. include:: ../requirements.txt


Using ts_Electrometer
=====================
This package is compatible with the scons build system and eups package management system.

.. code::

    setup -kr .
    scons
    scons install declare
    package-docs build
    python bin/RunElectrometer.py 1

Developing ts_Electrometer
==========================
Developing the ts_Electrometer package follows the `TSSW developer guide <https://tssw-developer.lsst.io>`_.
Code style is PEP-8 compliant with a few exceptions.
Flake8 is a tool given by the development docker image for checking PEP-8 compliance.
The setup.cfg file comes with the necessary exceptions already configured.
Developing with docker is described in the TSSW Developer guide.
`ts_salobj Documentation <https://ts-salobj.lsst.io>`_ will help you develop the CSC.
Writing unit tests is done by using the unittest module style.

There is a mock_server module.
Its not fully fleshed out yet.
Currently you create a ``socat`` virtual serial port, then start the mock server using the master port as the argument.
Commands can then be sent to the slave port and ideally any electrometer commands would respond similar to the real thing.
However, the only command that's really implemented is the ``*IDN`` command.

Contributing
============
ts_Electrometer is developed on `github <https://github.com/lsst-ts/ts_electrometer2>`_.
Use the `JIRA labels <https://jira.lsstcorp.org/issues/?jql=project%20%3D%20DM%20AND%20labels%20%20%3D%20ts_electrometer2>`_ to look for issues.
Here's  the `CI <https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_electrometer2/>`_.

.. automodapi:: lsst.ts.electrometer
    :no-main-docstr:
    :no-inheritance-diagram:

.. automodapi:: lsst.ts.electrometer.commands_factory
    :no-main-docstr:
    :no-inheritance-diagram:

.. automodapi:: lsst.ts.electrometer.controller
    :no-main-docstr:
    :no-inheritance-diagram:

.. automodapi:: lsst.ts.electrometer.csc
    :no-main-docstr:
    :no-inheritance-diagram:

.. automodapi:: lsst.ts.electrometer.enums
    :no-main-docstr:
    :no-inheritance-diagram:

.. automodapi:: lsst.ts.electrometer.mock_server
    :no-main-docstr:
    :no-inheritance-diagram:
