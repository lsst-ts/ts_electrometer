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
