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
$id: https://github.com/lsst-ts/ts_electrometer/blob/master/schema/Electrometer.yaml
title: Electrometer v6
description: Schema for Electrometer configuration files.
definitions:
  electrometer_specific_schema:
    type: object
    required:
      - sal_index
      - fits_files_path
      - mode
      - range
      - integration_time
      - median_filter_active
      - filter_active
      - avg_filter_active
      - tcp_port
      - host
      - timeout
      - brand
      - model_id
      - location
      - sensor_brand
      - sensor_model
      - sensor_serial
      - vsource_attached
      - temperature_attached
      - image_service_url
      - s3_instance
    additional_properties: false
    properties:
      sal_index:
        type: number
        minValue: 1
        description: The SAL Component index.
      fits_files_path:
        description: The path of where the fits file are written to disk.
        type: string
      mode:
        description: The scanning mode of the Electrometer.
        type: integer
      range:
        description: The value that the Electrometer scans around.
        type: number
      integration_time:
        description: The time that the electrometer opens per scan.
        type: number
      median_filter_active:
        description: Is the median filter active?
        type: boolean
      filter_active:
        description: Is the filter active?
        type: boolean
      avg_filter_active:
        description: Is the avg filter active?
        type: boolean
      tcp_port:
        description: The port that the moxa terminal server uses.
        type: integer
      host:
        description: The ip or hostname address for the electrometer.
        type: string
        format: hostname
      timeout:
        description: The timeout of the serial connection.
        type: integer
      brand:
        description: The brand of the electrometer.
        type: string
      model_id:
        description: The model ID for the electrometer.
        type: string
      location:
        description: The location where the electrometer is placed.
        type: string
      sensor_brand:
        description: The brand of the photodiode sensor.
        type: string
      sensor_model:
        description: The model of the photodiode sensor.
        type: string
      sensor_serial:
        description: The serial number of the photodiode sensor.
        type: string
      vsource_attached:
        description: Is the physical voltage output attached?
        type: boolean
      temperature_attached:
        description: Is the temperature probe attached?
        type: boolean
      image_service_url:
        description: The URL for the image service name host.
        type: string
      s3_instance:
        description: Denotes which S3 bucket to use.
        type: string
        enum: [tuc, ls, cp]
type: object
properties:
  electrometer_config:
    type: array
    items:
      "$ref": "#/definitions/electrometer_specific_schema"
required: [electrometer_config]
additional_properties: false
"""
)
"""Configuration schema as a constant."""
