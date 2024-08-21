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

CONFIG_SCHEMA = yaml.safe_load(
    """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_electrometer/blob/main/schema/Electrometer.yaml
title: Electrometer v7
description: Schema for Electrometer configuration files.
type: object
properties:
  instances:
    type: array
    items:
      type: object
      properties:
        sal_index:
          type: integer
          minValue: 1
        mode:
          type: integer
        range:
          type: number
        tcpip:
          type: object
          properties:
            hostname:
              type: string
            port:
              type: integer
            timeout:
              type: integer
          required:
            - hostname
            - port
            - timeout
          additionalProperties: false
        s3_instance:
          type: string
          enum:
            - tuc
            - ls
            - cp
        fits_file_path:
          type: string
        image_name_service:
          type: string
        filters:
          type: object
          properties:
            median:
              type: boolean
            average:
              type: boolean
            general:
              type: boolean
          required:
            - median
            - average
            - general
          additionalProperties: false
        sensor:
          type: object
          properties:
            brand:
              type: string
            model:
              type: string
            serial_number:
              type: string
          required:
            - brand
            - model
            - serial_number
          additionalProperties: false
        accessories:
          type: object
          properties:
            vsource:
              type: boolean
            temperature:
              type: boolean
          required:
            - vsource
            - temperature
          additionalProperties: false
        location:
          type: string
        integration_time:
          type: number
        electrometer_type:
          type: string
          enum:
            - Keithley
            - Keysight
        electrometer_model:
          type: string
        electrometer_config:
          type: object
      required:
        - sal_index
        - mode
        - range
        - tcpip
        - s3_instance
        - fits_file_path
        - image_name_service
        - filters
        - sensor
        - accessories
        - location
        - integration_time
        - electrometer_type
        - electrometer_model
        - electrometer_config
      additionalProperties: false
"""
)
# """Configuration schema as a constant."""
