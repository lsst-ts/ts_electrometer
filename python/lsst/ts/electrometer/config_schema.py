# This file is part of ts_electrometer.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
__all__ = ["CONFIG_SCHEMA"]

import yaml

CONFIG_SCHEMA: str = yaml.safe_load(
    """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_electrometer2/blob/master/schema/Electrometer.yaml
title: Electrometer v3
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
  tcp_port:
    description: the location of the USB mount for the electrometer
    type: integer
    default: 9999
  host:
    description: The ip or hostname address for the electrometer
    type: string
    format: hostname
    default: 127.0.0.1
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
