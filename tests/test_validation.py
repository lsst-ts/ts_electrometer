# This file is part of ts_electrometer.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import pathlib
import unittest

import jsonschema
import jsonschema.exceptions
import yaml

from lsst.ts import electrometer, salobj

TEST_CONFIG_DIR = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config")


class ValidationTestCase(unittest.TestCase):
    def setUp(self):
        self.config_schema = electrometer.CONFIG_SCHEMA
        self.validator = salobj.DefaultingValidator(self.config_schema)
        self.keithley_validator = salobj.DefaultingValidator(
            electrometer.KeithleyElectrometerController.get_config_schema()
        )
        self.keysight_validator = salobj.DefaultingValidator(
            electrometer.KeysightElectrometerController.get_config_schema()
        )

    def test_good_configuration(self):
        with open(TEST_CONFIG_DIR / "_init.yaml") as stream:
            config = yaml.safe_load(stream)
        self.validator.validate(config)
        for instance in config["instances"]:
            electrometer_config = instance["electrometer_config"]
            match instance["electrometer_type"]:
                case "Keithley":
                    self.keithley_validator.validate(electrometer_config)
                case "Keysight":
                    self.keysight_validator.validate(electrometer_config)

    def test_bad_configuration(self):
        with open(TEST_CONFIG_DIR / "bad_config.yaml") as stream:
            config = yaml.safe_load(stream)
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            self.validator.validate(config)

    def test_bad_electrometer_config(self):
        with open(TEST_CONFIG_DIR / "bad_config_2.yaml") as stream:
            config = yaml.safe_load(stream)
        self.validator.validate(config)
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            for instance in config["instances"]:
                electrometer_config = instance["electrometer_config"]
                match instance["electrometer_type"]:
                    case "Keithley":
                        self.keithley_validator.validate(electrometer_config)
                    case "Keysight":
                        self.keysight_validator.validate(electrometer_config)
