###############
ts_electrometer
###############

The Electrometer is a CSC for the Vera C. Rubin Observatory.
It is part of the Observatory Control System.
It measures the amount of light within a given space.

Installation
============
.. code::

    setup -kr .
    scons python

.. code::

    pip install .[dev]


Usage
=====

.. code::

    from lsst.ts import salobj

    domain = salobj.Domain()

    electrometer = salobj.Remote(name="Electrometer", domain=domain, index=1)

    await electrometer.start_task

.. code::

    await electrometer.cmd_startScan.set_start(timeout=10)
    await electrometer.cmd_stopScan.set_start(timeout=10)

Support
=======
Open issues in the jira project.

Roadmap
=======
N/A

Contributing
============
Contributions are welcome.
Please open issues in the jira project.
Make sure to contact the developer(s) and product owner(s) if unsure about something.

License
=======
The project is licensed under the GPLv3 license.
