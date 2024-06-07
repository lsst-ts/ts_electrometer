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

import logging
import os
import pathlib
import shutil
import unittest
import unittest.mock

import pytest
from lsst.ts import electrometer, salobj

STD_TIMEOUT = 20
TEST_CONFIG_DIR = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config")


@pytest.mark.skip("DM-40055")
class KeysightTestCase(salobj.BaseCscTestCase, unittest.IsolatedAsyncioTestCase):
    def tearDown(self) -> None:
        file_path = "/tmp/electrometerFitsFiles"
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

    def setUp(self) -> None:
        os.environ["LSST_SITE"] = "test"
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
            name="Electrometer", index=2, exe_name="run_electrometer"
        )

    async def test_standard_state_transitions(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            index=2,
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
                    "setVoltageSource",
                ]
            )

    async def test_perform_zero_calib(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=2,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_performZeroCalib.set_start(timeout=STD_TIMEOUT)

    async def test_set_digital_filter(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=2,
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
            await self.assert_next_sample(
                topic=self.remote.evt_digitalFilterChange,
                activateMedianFilter=True,
                activateFilter=True,
                activateAverageFilter=False,
            )

    async def test_set_integration_time(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=2,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setIntegrationTime.set_start(
                intTime=0.01, timeout=STD_TIMEOUT
            )
            topic = await self.assert_next_sample(topic=self.remote.evt_integrationTime)
            self.assertAlmostEqual(topic.intTime, 0.01)

    async def test_set_mode(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=2,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setMode.set_start(mode=2, timeout=STD_TIMEOUT)
            await self.assert_next_sample(topic=self.remote.evt_measureType, mode=2)

    async def test_set_range(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=2,
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
            index=2,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.csc.controller.image_service_client.get_next_obs_id = (
                unittest.mock.AsyncMock(return_value=([1], ["EM1_O_20221130_000001"]))
            )
            await self.remote.cmd_startScan.set_start(timeout=STD_TIMEOUT)

    async def test_start_scan_dt(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=2,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.csc.controller.image_service_client.get_next_obs_id = (
                unittest.mock.AsyncMock(return_value=([2], ["EM1_O_20221130_000002"]))
            )
            await self.remote.cmd_startScanDt.set_start(
                scanDuration=2, timeout=STD_TIMEOUT
            )

            await self.assert_next_sample(
                topic=self.remote.evt_largeFileObjectAvailable
            )

    async def test_set_voltage_source(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=2,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setVoltageSource.set_start(
                status=True, range=1, voltage_limit=2, level=2
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=0,
                level=0,
                range=0,
                status=True,
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=2,
                level=0,
                range=0,
                status=True,
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=2,
                level=0,
                range=1,
                status=True,
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=2,
                level=2,
                range=1,
                status=True,
            )


class ElectrometerCscTestCase(salobj.BaseCscTestCase, unittest.IsolatedAsyncioTestCase):
    def tearDown(self) -> None:
        file_path = "/tmp/electrometerFitsFiles"
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

    def setUp(self) -> None:
        os.environ["LSST_SITE"] = "test"
        self.log = logging.getLogger(type(self).__name__)
        return super().setUp()

    def basic_make_csc(self, initial_state, config_dir, simulation_mode, index):
        return electrometer.ElectrometerCsc(
            initial_state=initial_state,
            config_dir=config_dir,
            simulation_mode=simulation_mode,
            index=index,
        )

    @pytest.mark.skip("DM-40055")
    async def test_bin_script(self):
        await self.check_bin_script(
            name="Electrometer", index=1, exe_name="run_electrometer"
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
                    "setVoltageSource",
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
            self.csc.controller.image_service_client.get_next_obs_id = (
                unittest.mock.AsyncMock(return_value=([1], ["EM1_O_20221130_000001"]))
            )
            await self.remote.cmd_startScan.set_start(timeout=STD_TIMEOUT)

    async def test_start_scan_dt(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.csc.controller.image_service_client.get_next_obs_id = (
                unittest.mock.AsyncMock(return_value=([2], ["EM1_O_20221130_000002"]))
            )
            await self.remote.cmd_startScanDt.set_start(scanDuration=2)

            # await self.remote.evt_largeFileObjectAvailable.next(flush=False,
            #                                                     timeout=10)

    async def test_set_voltage_source(self):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=1,
            simulation_mode=1,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setVoltageSource.set_start(
                status=True, range=1, voltage_limit=2, level=2
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=0,
                level=0,
                range=0,
                status=True,
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=2,
                level=0,
                range=0,
                status=True,
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=2,
                level=0,
                range=1,
                status=True,
            )
            await self.assert_next_sample(
                topic=self.remote.evt_voltageSourceChanged,
                voltage_limit=2,
                level=2,
                range=1,
                status=True,
            )


if __name__ == "__main__":
    unittest.main()
