###############
ts_electrometer
###############

The Electrometer CSC is used to control a Keithley 6417b Electrometer which are used to monitor photodiodes throughout the Vera C. Rubin Observatory.
The photodiode is used to measure the intensity of light sources.
The photons release electrons in the photodiode, which get readout and quantified by the electrometer.
The primary use-case of the photodiode+electrometer system is for the calibration (flat field) screens for both the main and auxiliary telescopes.

`Documentation <https://ts-electrometer.lsst.io>`_

Installation
============
.. code::

    setup -kr .
    scons

.. code::

    pip install .[dev]

.. code::

    git config core.hooksPath .githooks


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
