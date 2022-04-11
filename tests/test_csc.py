import unittest
import os
import pathlib
import logging

import pytest

from lsst.ts import salobj, electrometer


STD_TIMEOUT = 10
TEST_CONFIG_DIR = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config")


class ElectrometerCscTestCase(unittest.IsolatedAsyncioTestCase, salobj.BaseCscTestCase):
    def setUp(self) -> None:
        os.environ["LSST_SITE"] = "electrometer"
        self.log = logging.getLogger(type(self).__name__)
        return super().setUp()

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
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.check_standard_state_transitions(
                enabled_commands=[
                    "performZeroCalib",
                    "setDigitalFilter",
                    "setIntegrationTime",
                    "setMode",
                    "setRange",
                    "startScan",
                    "startScanDt",
                    "stopScan",
                ]
            )



    async def test_perform_zero_calib(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_performZeroCalib.set_start(timeout=STD_TIMEOUT)

    async def test_set_digital_filter(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.remote.evt_digitalFilterChange.flush()
            await self.remote.cmd_setDigitalFilter.set_start(
                activateFilter=True,
                activateAvgFilter=False,
                activateMedFilter=True,
                timeout=STD_TIMEOUT,
            )

    async def test_set_integration_time(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setIntegrationTime.set_start(
                intTime=0.01, timeout=STD_TIMEOUT
            )

    async def test_set_mode(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setMode.set_start(mode=2, timeout=STD_TIMEOUT)

    @pytest.mark.skip("DM-????")
    async def test_set_range(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.remote.evt_measureRange.flush()
            await self.remote.cmd_setRange.set_start(setRange=0.1, timeout=STD_TIMEOUT)
            await self.assert_next_sample(
                topic=self.remote.evt_measureRange, rangeValue=0.1
            )

    async def test_start_scan(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_startScan.set_start(timeout=STD_TIMEOUT)

    @pytest.mark.skip("DM-33990")
    async def test_start_scan_dt(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED, index=1, simulation_mode=1
        ):
            await self.remote.cmd_startScanDt.set_start(scanDuration=2)


if __name__ == "__main__":
    unittest.main()
