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
import tempfile
import unittest
import unittest.mock

import parameterized

from lsst.ts import electrometer, salobj
from lsst.ts.electrometer import controller, enums
from lsst.ts.xml.enums.Electrometer import DetailedState

STD_TIMEOUT = 20
TEST_CONFIG_DIR = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config")
INDICES = [101, 103]


class CscTestCase(salobj.BaseCscTestCase, unittest.IsolatedAsyncioTestCase):
    def tearDown(self) -> None:
        file_path = "/tmp/electrometerFitsFiles"
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

    def setUp(self) -> None:
        os.environ["LSST_SITE"] = "test"
        self.log = logging.getLogger(type(self).__name__)
        self.sleep_patches = [
            unittest.mock.patch.object(controller, "SLEEP", 0),
            unittest.mock.patch.object(controller, "ZERO_CALIBRATION_DELAY", 0),
        ]
        for patch in self.sleep_patches:
            patch.start()
            self.addCleanup(patch.stop)
        return super().setUp()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        await salobj.delete_kafka_topics()

    def basic_make_csc(self, initial_state, config_dir, simulation_mode, index):
        return electrometer.ElectrometerCsc(
            initial_state=initial_state,
            config_dir=config_dir,
            simulation_mode=simulation_mode,
            index=index,
        )

    async def test_bin_script(self):
        await self.check_bin_script(name="Electrometer", index=INDICES[0], exe_name="run_electrometer")

    @parameterized.parameterized.expand(INDICES)
    async def test_standard_state_transitions(self, index):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            index=index,
            simulation_mode=2,
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
                    "changeNPLC",
                ]
            )

    async def test_fault_if_no_id_response_during_connect(self):
        with unittest.mock.patch.object(
            controller.KeithleyElectrometerController,
            "send_command",
            new=unittest.mock.AsyncMock(side_effect=TimeoutError("No ID response")),
        ):
            async with self.make_csc(
                initial_state=salobj.State.STANDBY,
                index=103,
                simulation_mode=2,
                config_dir=TEST_CONFIG_DIR,
            ):
                await self.assert_next_sample(
                    topic=self.remote.evt_summaryState,
                    summaryState=salobj.State.STANDBY,
                )
                await self.assert_next_sample(
                    topic=self.remote.evt_errorCode,
                    errorCode=0,
                )

                await self.remote.cmd_start.set_start(timeout=STD_TIMEOUT)

                await self.assert_next_sample(
                    topic=self.remote.evt_summaryState,
                    summaryState=salobj.State.FAULT,
                )
                await self.assert_next_sample(
                    topic=self.remote.evt_errorCode,
                    errorCode=enums.Error.CONNECTION,
                )

    @parameterized.parameterized.expand(INDICES)
    async def test_perform_zero_calib(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.assert_next_sample(
                topic=self.remote.evt_detailedState,
                detailedState=DetailedState.NOTREADINGSTATE,
            )
            await self.remote.cmd_performZeroCalib.set_start(timeout=STD_TIMEOUT)

    @parameterized.parameterized.expand(INDICES)
    async def test_set_digital_filter(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.assert_next_sample(
                topic=self.remote.evt_detailedState,
                detailedState=DetailedState.NOTREADINGSTATE,
            )
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
            await self.assert_next_sample(
                topic=self.remote.evt_detailedState, detailedState=DetailedState.CONFIGURINGSTATE
            )
            await self.assert_next_sample(
                topic=self.remote.evt_detailedState,
                detailedState=DetailedState.NOTREADINGSTATE,
            )

    @parameterized.parameterized.expand(INDICES)
    async def test_set_integration_time(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setIntegrationTime.set_start(intTime=0.02, timeout=STD_TIMEOUT)
            topic1 = await self.assert_next_sample(topic=self.remote.evt_integrationTime)
            self.assertAlmostEqual(topic1.intTime, 0.01)
            topic2 = await self.assert_next_sample(topic=self.remote.evt_integrationTime)
            self.assertAlmostEqual(topic2.intTime, 0.02)

    @parameterized.parameterized.expand(INDICES)
    async def test_set_mode(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.assert_next_sample(topic=self.remote.evt_measureType, mode=1)
            await self.remote.cmd_setMode.set_start(mode=2, timeout=STD_TIMEOUT)
            await self.assert_next_sample(topic=self.remote.evt_measureType, mode=2)
            await self.remote.cmd_setMode.set_start(mode=3, timeout=STD_TIMEOUT)
            await self.assert_next_sample(topic=self.remote.evt_measureType, mode=3)
            await self.remote.cmd_setMode.set_start(mode=4, timeout=STD_TIMEOUT)
            await self.assert_next_sample(topic=self.remote.evt_measureType, mode=4)

    @parameterized.parameterized.expand(INDICES)
    async def test_set_range(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.remote.evt_measureRange.flush()
            await self.remote.cmd_setRange.set_start(setRange=0.1, timeout=STD_TIMEOUT)
            data = await self.assert_next_sample(topic=self.remote.evt_measureRange)
            self.assertAlmostEqual(data.rangeValue, 0.1)

    @parameterized.parameterized.expand(INDICES)
    async def test_start_scan(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.csc.image_name_service_client.get_next_obs_id = unittest.mock.AsyncMock(
                return_value=([1], ["EM1_O_20221130_000001"])
            )
            self.remote.evt_detailedState.flush()
            await self.remote.cmd_startScan.set_start(timeout=STD_TIMEOUT)
            await self.assert_next_sample(
                topic=self.remote.evt_detailedState,
                detailedState=DetailedState.MANUALREADINGSTATE,
            )

    @parameterized.parameterized.expand(INDICES)
    async def test_start_scan_dt(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            self.csc.image_name_service_client.get_next_obs_id = unittest.mock.AsyncMock(
                return_value=([2], ["EM1_O_20221130_000002"])
            )
            await self.remote.cmd_startScanDt.set_start(scanDuration=0.1, timeout=STD_TIMEOUT)

            await self.assert_next_sample(topic=self.remote.evt_largeFileObjectAvailable)

    async def test_start_scan_dt_falls_back_to_local_file_if_upload_fails(self):
        obs_id = "EM1_O_20221130_000003"
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=103,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            with tempfile.TemporaryDirectory() as tmpdir:
                self.csc.fits_file_path = tmpdir
                self.csc.image_name_service_client.get_next_obs_id = unittest.mock.AsyncMock(
                    return_value=([3], [obs_id])
                )
                self.csc.bucket.upload = unittest.mock.AsyncMock(side_effect=RuntimeError("upload failed"))

                await self.remote.cmd_startScanDt.set_start(scanDuration=0.1, timeout=STD_TIMEOUT)

                local_file = pathlib.Path(tmpdir).joinpath(f"{obs_id}.fits")
                self.assertTrue(local_file.exists())
                self.assertGreater(local_file.stat().st_size, 0)

    @parameterized.parameterized.expand(INDICES)
    async def test_set_voltage_source(self, index):
        async with self.make_csc(
            initial_state=salobj.State.ENABLED,
            index=index,
            simulation_mode=2,
            config_dir=TEST_CONFIG_DIR,
        ):
            await self.remote.cmd_setVoltageSource.set_start(status=True, range=1, voltage_limit=2, level=2)
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
