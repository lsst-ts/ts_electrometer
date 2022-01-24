__all__ = ["CONFIG_SCHEMA"]

import yaml


CONFIG_SCHEMA = yaml.safe_load(
    """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_electrometer2/blob/master/schema/Electrometer.yaml
title: Electrometer v2
description: Schema for Electrometer configuration files
type: object
properties:
  fits_files_path:
    description: The path of where the fits file are written to disk.
    type: string
    default: "~develop/electrometerFitsFiles"
  mode:
    description: The scanning mode of the Electrometer
    type: integer
    default: 1
  range:
    description: Something
    type: number
    default: -0.01
  integration_time:
    description: The time that the electrometer opens per scan.
    type: number
    default: 0.01
  median_filter_active:
    description: Is the median filter active?
    type: boolean
    default: false
  filter_active:
    description: Is the filter active?
    type: boolean
    default: true
  avg_filter_active:
    description: Is the avg filter active?
    type: boolean
    default: false
  serial_port:
    description: the location of the USB mount for the the electrometer
    type: string
    default: "/dev/electrometer"
  baudrate:
    description: The baudrate of the serial connection.
    type: integer
    default: 57600
  timeout:
    description: The timeout of the serial connection.
    type: integer
    default: 2
"""
)
"""Configuration schema as a constant."""
