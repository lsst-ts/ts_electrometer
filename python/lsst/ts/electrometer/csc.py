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

__all__ = ["execute_csc", "command_csc", "ElectrometerCsc"]

import asyncio
import types

from lsst.ts import salobj, utils
from lsst.ts.xml.enums.Electrometer import DetailedState

from . import __version__, controller, enums, mock_server
from .config_schema import CONFIG_SCHEMA


def execute_csc() -> None:
    asyncio.run(ElectrometerCsc.amain(index=True))


def command_csc() -> None:
    asyncio.run(salobj.CscCommander.amain(name="Electrometer", index=True))


class ElectrometerCsc(salobj.ConfigurableCsc):
    """Class that implements the CSC for the electrometer.

    Parameters
    ----------
    index : `int`
        The index of the CSC.
    config_dir : `str`
        Path to config directory.
        One is provided for you in another method.
    initial_state : `lsst.ts.salobj.State`
        The initial state of the CSC.
        Should be used for unit tests and development.
    simulation_mode : `int`
        The simulation mode of the CSC.

    Attributes
    ----------
    controller : `ElectrometerController`
        The controller object for the electrometer.
    run_event_loop : `bool`
        Whether the event loop runs.
    event_loop_task : `asyncio.Task`
        A task for handling the event loop.
        Currently not implemented.
    default_force_output : `bool`
        Force the output of an event.
    bucket : `None` or `salobj.AsyncS3Bucket`
    """

    valid_simulation_modes = (0, 1, 2)
    version = __version__

    def __init__(
        self,
        index,
        config_dir=None,
        initial_state=salobj.State.STANDBY,
        simulation_mode=0,
    ):
        super().__init__(
            name="Electrometer",
            index=index,
            config_schema=CONFIG_SCHEMA,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
        )
        self.simulator = None
        self.run_event_loop = False
        self.event_loop_task = utils.make_done_future()
        self.default_force_output = True
        self.bucket = None
        self.controller = None
        self.log.debug("finished initializing")

    def assert_substate(self, substates, action):
        """Assert the CSC is in the proper substate.

        Parameters
        ----------
        substates : `list` of `Electrometer.DetailedState`
            The list of accepted substates for a given command.
        action : `str`
            The name of the command to assert.

        Raises
        ------
        salobj.ExpectedError
            If the current substate is not allowed to preform the action.
        """
        if self.detailed_state not in [
            DetailedState(substate) for substate in substates
        ]:
            raise salobj.ExpectedError(
                f"command not allowed in {self.detailed_state!r}"
            )

    @property
    def detailed_state(self):
        """The current substate of the CSC.

        Returns
        -------
        detailed_state : `lsst.ts.xml.enums.Electrometer.DetailedState`
            The sub state of the CSC.
        """
        return self.evt_detailedState.data.detailedState

    async def report_detailed_state(self, new_state):
        """Report the new detailed state."""
        await self.evt_detailedState.set_write(detailedState=new_state)

    async def configure(self, config):
        """Configure the Electrometer CSC.

        Parameters
        ----------
        config : `types.SimpleNamespace`
            The parsed yaml object.
        """
        for instance in config.instances:
            if instance["sal_index"] == self.salinfo.index:
                break
        if instance["sal_index"] != self.salinfo.index:
            raise RuntimeError(f"No configuration found for {self.salinfo.index=}")
        self.log.debug(f"instance is {instance}")
        self.log.debug(f'electrometer type is {instance["electrometer_type"]}')
        electrometer_type = instance["electrometer_type"]
        controller_class = getattr(
            controller, f"{electrometer_type}ElectrometerController"
        )
        self.validator = salobj.DefaultingValidator(
            controller_class.get_config_schema()
        )
        # self.validator.validate(instance)
        self.controller = controller_class(csc=self, log=self.log)
        self.controller.configure(types.SimpleNamespace(**instance))
        self.log.debug(f"brand={electrometer_type}")

    async def handle_summary_state(self):
        """Handle the summary of the CSC.

        If transitioning to the disabled or enabled state

        * Start the simulator if simulation_mode is true.
        * Create a bucket object for LFA support.
        * Connect to the server if it is not connected already.

        If leaving the disabled state

        * Disconnect from the server, if connected.
        * If the simulator is running, stop it.
        """
        do_mock = False
        create = False
        if self.disabled_or_enabled:
            if self.simulation_mode and self.simulator is None:
                self.simulator = mock_server.MockServer(
                    self.controller.electrometer_type
                )
                await self.simulator.start_task
                self.controller.commander.host = self.simulator.host
                self.controller.commander.port = self.simulator.port
            if self.simulation_mode == 2:
                do_mock = True
                create = True
            if self.bucket is None:
                try:
                    self.bucket = salobj.AsyncS3Bucket(
                        salobj.AsyncS3Bucket.make_bucket_name(
                            s3instance=self.controller.s3_instance
                        ),
                        create=create,
                        domock=do_mock,
                    )
                except Exception:
                    self.log.exception("Bucket creation failed.")
                    await self.fault(
                        code=enums.Error.BUCKET, report="Bucket creation failed."
                    )
                    return
            if not self.controller.connected:
                try:
                    await self.controller.connect()
                except Exception:
                    self.log.exception("Connection failed.")
                    await self.fault(
                        code=enums.Error.CONNECTION, report="Connection failed."
                    )
                    return
        else:
            if self.controller is not None:
                if self.controller.connected:
                    await self.controller.disconnect()
            if self.simulator is not None:
                await self.simulator.close()
                self.simulator = None

    async def do_performZeroCalib(self, data):
        """Perform zero calibration.

        Parameters
        ----------
        data : `cmd_performZeroCalib.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE],
            action="performZeroCalib",
        )
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            await self.controller.perform_zero_calibration(
                mode=None, auto=None, set_range=None, integration_time=None
            )
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
            self.log.info("Zero Calibration Completed")
        except Exception:
            self.log.exception("performZeroCalibration failed.")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_setDigitalFilter(self, data):
        """Set the digital filter(s).

        Parameters
        ----------
        data : `cmd_setDigitalFilter.DataType`
            The data for the command.
        """
        self.log.debug("setDigitalFilter Started")
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE],
            action="setDigitalFilter",
        )
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            await self.controller.set_digital_filter(
                activate_filter=data.activateFilter,
                activate_avg_filter=data.activateAvgFilter,
                activate_med_filter=data.activateMedFilter,
            )
            self.log.debug("setDigitalFilter controller interaction completed")
            self.log.debug(
                f"filter_active={self.controller.filter_active},"
                f"avg_filter_active={self.controller.avg_filter_active},"
                f"median_filter_active={self.controller.median_filter_active}"
            )
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
            self.log.info("setDigitalFilter Completed")
        except Exception:
            self.log.exception("setDigitalFilter failed.")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_setIntegrationTime(self, data):
        """Set the integration time.

        Parameters
        ----------
        data : `cmd_setIntegrationTime.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE],
            action="setIntegrationTime",
        )
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            await self.controller.set_integration_time(int_time=data.intTime)
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
            self.log.exception("setIntegrationTime failed.")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_setMode(self, data):
        """Set the mode/unit.

        Parameters
        ----------
        data : `cmd_setMode.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE], action="setMode"
        )
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            self.log.debug(f"Setting mode: {data.mode}")
            await self.controller.set_mode(mode=data.mode)
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
            self.log.exception("setMode failed.")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_setRange(self, data):
        """Set the range.

        Parameters
        ----------
        data : `cmd_setRange.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE], action="setRange"
        )
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            await self.controller.set_range(set_range=data.setRange)
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
            self.log.exception("setRange failed.")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_startScan(self, data):
        """Start scan.

        Parameters
        ----------
        data : `cmd_startScan.DataType`
            The data for the command.
        """
        self.log.debug("Starting startScan")
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE], action="startScan"
        )
        try:
            await self.report_detailed_state(DetailedState.MANUALREADINGSTATE)
            await self.controller.start_scan(group_id=getattr(data, "groupId", None))
            self.log.debug("startScan Completed")
        except Exception as e:
            msg = "startScanDt failed."
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
            await self.fault(code=enums.Error.FILE_ERROR, report=f"{msg}: {repr(e)}")

    async def do_startScanDt(self, data):
        """Start the scan with a set duration.

        Parameters
        ----------
        data : `cmd_startScanDt.DataType`
            The data for the command.
        """
        self.log.debug("Starting startScanDt")
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE], action="startScanDt"
        )
        try:
            await self.report_detailed_state(DetailedState.SETDURATIONREADINGSTATE)
            await self.controller.start_scan_dt(
                scan_duration=data.scanDuration, group_id=getattr(data, "groupId", None)
            )
            await self.report_detailed_state(DetailedState.READINGBUFFERSTATE)
            await self.cmd_startScanDt.ack_in_progress(
                data=data, timeout=data.scanDuration, result=""
            )
            await self.controller.stop_scan()
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception as e:
            msg = "startScanDt failed."
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
            await self.fault(code=enums.Error.FILE_ERROR, report=f"{msg}: {repr(e)}")

        self.log.info("startScanDt Completed")

    async def do_stopScan(self, data):
        """Stop the scan.

        Parameters
        ----------
        data : `cmd_stopScan.DataType`
            The data for the command.
        """
        self.log.debug("Starting stopScan")
        self.assert_enabled()
        self.assert_substate(
            substates=[
                DetailedState.MANUALREADINGSTATE,
                DetailedState.SETDURATIONREADINGSTATE,
            ],
            action="stopScan",
        )
        try:
            await self.report_detailed_state(DetailedState.READINGBUFFERSTATE)
            self.log.debug("detailed state reported")
            await self.controller.stop_scan()
            self.log.debug("controller stopped scan")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
            self.log.info("stopScan Completed")
        except Exception as e:
            msg = "stopScan failed."
            self.log.exception("stopScan failed.")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
            await self.fault(code=enums.Error.FILE_ERROR, report=f"{msg}: {repr(e)}")

    async def do_setVoltageSource(self, data):
        self.assert_enabled()
        self.assert_substate(
            substates=[DetailedState.NOTREADINGSTATE], action="setRange"
        )
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            await self.controller.toggle_voltage_source(data.status)
            await self.controller.set_voltage_limit(data.voltage_limit)
            await self.controller.set_voltage_range(data.range)
            await self.controller.set_voltage_level(data.level)
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
            self.log.exception("SetVoltageSource failed.")
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    @staticmethod
    def get_config_pkg():
        """Get the config package.

        Returns
        -------
        str
            The name of the package where the configuration is stored.
        """
        return "ts_config_ocs"

    async def close_tasks(self):
        """Close unfinished tasks when CSC is stopped."""
        await super().close_tasks()
        if self.controller is not None:
            await self.controller.disconnect()
        if self.simulator is not None:
            await self.simulator.close()
            self.simulator = None
