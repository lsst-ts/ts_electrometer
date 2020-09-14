.. _User_Guide:

#######################
Electrometer User Guide
#######################

This CSC is used to control Keithley 6417b electrometers.
The primary use-case is to read/monitor the electrical signals from a Hamamatsu S2281 photodiode, however it can be used with other devices.
The device is generally used in a current and charge measuring modes.
It communicates over RS-232 serial cable.
The computer that it is connected to uses a straight-through RS-232 to USB type A cable.

The device creates a FITS file.
It tracks time and intensity.
The fits files are stored on the disk of the docker container.

Electrometer Interface
======================

Link to the XML is located at the top of the :doc:`index </index>`.


Example Use-Case
================

The following example demonstrates how to instantiate a single electrometer, then perform a reading of an arbitrary length.

.. code::

    from lsst.ts import salobj
    
    domain = salobj.Domain()

    electrometer = salobj.Remote(name="Electrometer", domain=domain, index=1)

    await electrometer.start_task

.. code::

    await electrometer.cmd_performZeroCalib.set_start(timeout=10)
    await electrometer.cmd_setDigitalFilter.set_start(activateFilter=False, activateAvgFilter=False, activateMedFilter=False, timeout=10)
    await electrometer.cmd_startScan.set_start(timeout=10)
    await electrometer.cmd_stopScan.set_start(timeout=10)

.. code::

    await domain.close()
