.. _Configuration_details:

##########################
Electrometer Configuration
##########################

The Electrometer is configured with an ``instances`` list.
Each entry corresponds to one SAL index and defines the device type, network endpoint, default measurement settings, object-storage target, image name service, sensor metadata, and optional accessories.
The configuration files are located in the `ts_config_ocs repo <https://github.com/lsst-ts/ts_config_ocs>`_.

The `schema <https://github.com/lsst-ts/ts_electrometer/blob/main/python/lsst/ts/electrometer/config_schema.py>`_ for the configuration file is located within the repo.

Configuration Fields
====================

``sal_index``
    SAL index for this electrometer instance.

``mode``
    Default measurement mode.
    The numeric values correspond to the ``Electrometer.measureType`` enumeration: current, charge, voltage, and resistance.

``range``
    Default measurement range.

``tcpip``
    Network settings for the electrometer connection.
    The ``hostname`` and ``port`` usually identify the Moxa NPort or other serial-to-ethernet server.
    The ``timeout`` value is used as the default command timeout.

``s3_instance``
    S3 instance used for scan FITS file uploads.
    Supported values are ``tuc``, ``ls``, and ``cp``.

``fits_file_path``
    Local fallback path for FITS files.

``image_name_service``
    URL of the image name service used to allocate observation identifiers for scan products.

``filters``
    Default digital filter settings.
    The ``general`` setting enables filtering, while ``average`` and ``median`` select the filter algorithms.

``sensor``
    Sensor metadata written to the FITS header.
    This includes ``brand``, ``model``, and ``serial_number``.

``accessories``
    Optional trace fields.
    ``temperature`` enables temperature data and ``vsource`` enables voltage source data when supported by the configured device.

``location``
    Human-readable instrument location written to the FITS header.

``integration_time``
    Default integration time, in seconds.

``electrometer_type``
    Electrometer brand.
    Supported values are ``Keithley`` and ``Keysight``.

``electrometer_model``
    Electrometer model identifier written to the FITS header.

``electrometer_config``
    Device-specific configuration namespace.
    It is currently reserved for future Keithley- or Keysight-specific settings.

Example
-------

.. code-block:: yaml

    instances:
      - sal_index: 101
        mode: 1
        range: 2.0e-08
        tcpip:
          hostname: "electrometer-moxa.example.org"
          port: 4001
          timeout: 2
        s3_instance: "ls"
        fits_file_path: "/home/saluser/develop/electrometerFitsFiles"
        image_name_service: "http://ccs.lsst.org"
        filters:
          median: false
          general: false
          average: false
        sensor:
          brand: "Hamamatsu"
          model: "S2281"
          serial_number: "S22818D091"
        accessories:
          vsource: false
          temperature: false
        location: "Calibration Screen"
        integration_time: 0.1
        electrometer_type: "Keithley"
        electrometer_model: "6517b"
        electrometer_config: {}
