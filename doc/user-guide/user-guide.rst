.. _User_Guide:

#######################
Electrometer User Guide
#######################

The electrometer is a Keithley Spectrograph that measures the amount of electrons in proximity with a sensor.
It communicates over RS-232 serial cable.
The computer that it is connected to uses a RS-232 to USB type A cable.

Electrometer Interface
======================

Link to the XML is located at the top of the :doc:`index </index>`.


Example Use-Case
================

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
