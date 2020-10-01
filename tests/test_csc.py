import unittest

import asynctest

from lsst.ts import salobj, electrometer


class ElectrometerCscTestCase(asynctest.TestCase, salobj.BaseCscTestCase):
    def basic_make_csc(self, initial_state, config_dir, simulation_mode, index):
        return electrometer.ElectrometerCsc(
            initial_state=initial_state,
            config_dir=config_dir,
            simulation_mode=simulation_mode,
            index=index,
        )

    async def test_bin_script(self):
        await self.check_bin_script(
            name="Electrometer", index=1, exe_name="run_electrometer.py"
        )

    async def test_standard_state_transitions(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, index=1):
            await self.check_standard_state_transitions(
                enabled_commands=[
                    "performZeroCalibration",
                    "setDigitalFilter",
                    "setIntegrationTime",
                    "setMode",
                    "setRange",
                    "startScan",
                    "startScanDt",
                    "stopScan",
                ]
            )


if __name__ == "__main__":
    unittest.main()
