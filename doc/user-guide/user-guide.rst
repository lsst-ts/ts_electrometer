.. _User_Guide:

#######################
Electrometer User Guide
#######################

This CSC is used to control indexed Keithley and Keysight electrometers.
The primary use-case is to read/monitor the electrical signals from a Hamamatsu S2281 photodiode, however it can be used with other devices.
The device is generally used in current and charge measuring modes.
The CSC communicates over TCP/IP, either directly to an ethernet-capable electrometer or through a serial-to-ethernet terminal server.
The CSC creates a FITS file for each completed scan.
The FITS file records the measured signal, timestamps, and configured trace fields such as temperature or voltage source data when those accessories are enabled.
The file is uploaded through the configured S3 bucket and announced with the ``largeFileObjectAvailable`` event.

Electrometer Interface
======================

Link to the XML is located at the top of the :doc:`index </index>`.

Common Commands and Events
==========================

The normal scan workflow is:

#. Configure the device through the CSC configuration file.
#. Bring the CSC to ``ENABLED``.
#. Optionally issue configuration commands such as ``performZeroCalib``, ``setDigitalFilter``, ``setIntegrationTime``, ``changeNPLC``, ``setMode``, ``setRange``, or ``setVoltageSource``.
#. Start a manual scan with ``startScan`` and finish it with ``stopScan``.
   Alternatively, use ``startScanDt`` to acquire for a fixed duration.
#. Read the ``largeFileObjectAvailable`` event to find the uploaded FITS file.

The CSC publishes configuration changes through the corresponding events, including ``measureType``, ``measureRange``, ``integrationTime``, ``digitalFilterChange``, ``changedNPLC``, and ``voltageSourceChanged``.
The ``detailedState`` event reports whether the CSC is idle, configuring, reading, or reading out the buffer.

Example Use-Case
================

The following example demonstrates how to instantiate a single electrometer, then perform a reading of an arbitrary length.

.. code::

    from lsst.ts import salobj
    
    domain = salobj.Domain()

    electrometer = salobj.Remote(name="Electrometer", domain=domain, index=101)

    await electrometer.start_task

.. code::

    await electrometer.cmd_performZeroCalib.set_start(timeout=10)
    await electrometer.cmd_setDigitalFilter.set_start(activateFilter=False, activateAvgFilter=False, activateMedFilter=False, timeout=10)
    await electrometer.cmd_startScan.set_start(timeout=10)
    await electrometer.cmd_stopScan.set_start(timeout=60)
    lfo = await electrometer.evt_largeFileObjectAvailable.next(flush=False, timeout=60)
    print(lfo.url)

For a fixed-duration scan, use ``startScanDt`` instead of ``startScan`` and ``stopScan``:

.. code::

    await electrometer.cmd_startScanDt.set_start(scanDuration=5.0, timeout=60)
    lfo = await electrometer.evt_largeFileObjectAvailable.next(flush=False, timeout=60)
    print(lfo.url)

.. code::

    await domain.close()
