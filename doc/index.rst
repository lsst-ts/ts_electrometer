############
Electrometer
############

.. image:: https://img.shields.io/badge/SAL-API-gray.svg
    :target: https://ts-xml.lsst.io/sal_interfaces/Electrometer.html
.. image:: https://img.shields.io/badge/GitHub-gray.svg
    :target: https://github.com/lsst-ts/ts_electrometer
.. image:: https://img.shields.io/badge/Jira-gray.svg
    :target: https://jira.lsstcorp.org/issues/?jql=labels+%3D+ts_electrometer
.. image:: https://img.shields.io/badge/Jenkins-gray.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_electrometer/

.. _Overview:

Overview
========

The :ref:`Contact info <ts_xml:index:csc-table:Electrometer>` will show who the lead developer and product owner are.

The Electrometer is used in conjunction with a photodiode to measure the intensity of a light source.
The device supports multiple modes.
Generally, it is used in the modes that measure current and accumulated/integrated charge.
The electrometer is connected via ethernet, using a serial-ethernet terminal to a docker container running centos 7.
It is deployed as a docker container.
The component is indexable and so it is possible to command multiple electrometers simultaneously.

.. note:: If you are interested in viewing other branches of this repository append a `/v` to the end of the url link. For example `https://ts-electrometer.lsst.io/v/`


.. _User_Documentation:

User Documentation
==================

User-level documentation, found at the link below, is aimed at personnel looking to perform the standard use-cases/operations with the Electrometer.

.. toctree::
    user-guide/user-guide
    :maxdepth: 2

.. _Configuration:

Configuring the Electrometer
============================

The configuration for the Electrometer is described at the following link.

.. toctree::
    configuration/configuration
    :maxdepth: 1


.. _Development_Documentation:

Development Documentation
=========================

This area of documentation focuses on the classes used, API's, and how to participate to the development of the Electrometer software packages.

.. toctree::
    developer-guide/developer-guide
    :maxdepth: 1

.. _index:Version_History:

Version History
===============

The version history of the Electrometer is found at the following link.

.. toctree::
    version-history
    :maxdepth: 1
