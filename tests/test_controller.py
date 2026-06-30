import pathlib
import types
import unittest

import yaml

from lsst.ts.electrometer import controller

TEST_CONFIG = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config", "_init.yaml")


class ControllerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_configure_does_not_require_csc(self):
        with open(TEST_CONFIG) as fp:
            config = yaml.safe_load(fp)

        instance = next(item for item in config["instances"] if item["sal_index"] == 103)
        ctrl = controller.KeithleyElectrometerController()
        ctrl.configure(types.SimpleNamespace(**instance))

        self.assertFalse(hasattr(ctrl, "csc"))
        self.assertEqual(ctrl.commander.brand, "Keithley")
        self.assertEqual(ctrl.commander.hostname, "localhost")
        self.assertEqual(ctrl.commander.port, 4002)
        self.assertEqual(ctrl.mode, "CURR")


if __name__ == "__main__":
    unittest.main()
