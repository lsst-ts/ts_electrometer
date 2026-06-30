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

from dataclasses import dataclass

__all__ = ["execute_csc", "command_csc", "ElectrometerCsc"]

import asyncio
import pathlib
import types

from astropy.time import Time

from lsst.ts import salobj, utils
from lsst.ts.xml.enums.Electrometer import DetailedState

from . import __version__, controller, enums, mock_server
from .config_schema import CONFIG_SCHEMA

READ_DURATION = 20


def execute_csc() -> None:
    """Run the indexed Electrometer CSC."""
    asyncio.run(ElectrometerCsc.amain(index=True))


def command_csc() -> None:
    """Run the command-line commander for the indexed Electrometer CSC."""
    asyncio.run(salobj.CscCommander.amain(name="Electrometer", index=True))


@dataclass
class FitsData:
    """Metadata required to write a FITS file.

    Parameters
    ----------
    index : `int`
        SAL index of the CSC.
    name : `str`
        SAL component name.
    obs_ids : `list` [`str`]
        Observation identifiers allocated for the scan.
    """

    index: int
    name: str
    obs_ids: list[str]


CONTROLLER_CLASSES: dict[str, type[controller.ElectrometerController]] = {
    "Keithley": controller.KeithleyElectrometerController,
    "Keysight": controller.KeysightElectrometerController,
}


class ElectrometerCsc(salobj.ConfigurableCsc):
    """Implement the Electrometer CSC.

    Parameters
    ----------
    index : `int`
        The index of the CSC.
    config_dir : `str` or `None`, optional
        Path to the configuration directory.
    initial_state : `lsst.ts.salobj.State`, optional
        Initial summary state for the CSC.
    simulation_mode : `int`
        The simulation mode of the CSC.

    Attributes
    ----------
    simulator : `mock_server.MockServer` or `None`
        Electrometer simulator used for simulation modes.
    controller : `controller.ElectrometerController` or `None`
        Controller object for the configured electrometer.
    image_name_service_client : `lsst.ts.utils.ImageNameServiceClient` or
            `None`
        Client used to allocate observation identifiers for scan products.
    run_event_loop : `bool`
        Whether the event loop runs.
    event_loop_task : `asyncio.Task`
        Done future reserved for compatibility with existing task cleanup.
    default_force_output : `bool`
        Force the output of an event.
    bucket : `salobj.AsyncS3Bucket` or `None`
        Bucket used for large file object uploads.
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
        self.controller: controller.ElectrometerController | None = None
        self.image_name_service_client = None

    @property
    def active_bucket(self) -> salobj.AsyncS3Bucket:
        """Configured S3 bucket.

        Raises
        ------
        RuntimeError
            If the bucket has not been configured.
        """
        if self.bucket is None:
            raise RuntimeError("Bucket has not been configured")
        return self.bucket

    @property
    def active_controller(self) -> controller.ElectrometerController:
        """Configured electrometer controller.

        Raises
        ------
        RuntimeError
            If the controller has not been configured.
        """
        if self.controller is None:
            raise RuntimeError("Electrometer controller has not been configured")
        return self.controller

    @property
    def active_image_name_service_client(self) -> utils.ImageNameServiceClient:
        """Configured image name service client.

        Raises
        ------
        RuntimeError
            If the image name service client has not been configured.
        """
        if self.image_name_service_client is None:
            raise RuntimeError("Image name service client is not configured.")
        return self.image_name_service_client

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
        if self.detailed_state not in [DetailedState(substate) for substate in substates]:
            raise salobj.ExpectedError(f"command not allowed in {self.detailed_state!r}")

    def assert_valid_range(self):
        """Assert that the requested measurement range is supported."""
        # TODO DM-51208 Write method that asserts value is in valid range.
        pass

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
        """Report the detailed state.

        Parameters
        ----------
        new_state : `lsst.ts.xml.enums.Electrometer.DetailedState`
            Detailed state to publish.
        """
        await self.evt_detailedState.set_write(detailedState=new_state)

    async def write_scan_result(self, scan_result: controller.ScanResult) -> None:
        """Write scan data to object storage and publish the LFA event.

        Parameters
        ----------
        scan_result : `controller.ScanResult`
            Scan data and metadata returned by the active controller.
        """
        image_name_service_client = self.active_image_name_service_client
        _, obs_ids = await image_name_service_client.get_next_obs_id(num_images=1)
        fits_data = FitsData(index=self.salinfo.index, name=self.salinfo.name, obs_ids=obs_ids)
        controller = self.active_controller
        file = await controller.write_fits_file(
            scan_result=scan_result,
            data_format=scan_result.trace_elements,
            fits_data=fits_data,
        )
        bucket = self.active_bucket
        key_name = bucket.make_key(
            salname=self.salinfo.name,
            salindexname=self.salinfo.index,
            generator="fits",
            date=Time(scan_result.end_time, format="unix_tai"),
            other=obs_ids[0],
            suffix=".fits",
        )
        key_name = key_name[: key_name.rfind("/") + 1] + f"{obs_ids[0]}.fits"
        try:
            url = await bucket.upload(fileobj=file, key=key_name)
        except Exception:
            self.log.exception("Uploading file to S3 bucket failed.")
            file.seek(0)
            local_path = pathlib.Path(controller.fits_file_path).joinpath(f"{obs_ids[0]}.fits")
            try:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(file.read())
            except Exception as e:
                msg = "Writing file to local disk failed."
                self.log.exception(msg)
                raise RuntimeError(msg) from e
        else:
            await self.evt_largeFileObjectAvailable.set_write(
                url=url,
                id=scan_result.group_id,
                generator=f"{self.salinfo.name}:{self.salinfo.index}",
            )

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
        self.log.debug(f"electrometer type is {instance['electrometer_type']}")
        electrometer_type = instance["electrometer_type"]
        try:
            controller_class = CONTROLLER_CLASSES[electrometer_type]
        except KeyError as e:
            raise RuntimeError(f"Unsupported electrometer type: {electrometer_type!r}") from e
        self.validator = salobj.DefaultingValidator(controller_class.get_config_schema())
        # self.validator.validate(instance)
        self.controller = controller_class(log=self.log)
        self.controller.configure(types.SimpleNamespace(**instance))
        self.image_name_service_client = utils.ImageNameServiceClient(
            url=instance["image_name_service"],
            csc_index=self.salinfo.index,
            source="Electrometer",
        )
        self.log.debug(f"brand={electrometer_type}")

    async def handle_summary_state(self):
        """Handle transitions into and out of active summary states.

        If transitioning to the disabled or enabled state:

        * Start the simulator if simulation_mode is true.
        * Create a bucket object for LFA support.
        * Connect the controller to the electrometer if needed.
        * Publish the controller settings as SAL events.

        If leaving the disabled or enabled state:

        * Disconnect from the server, if connected.
        * If the simulator is running, stop it.
        """
        do_mock = False
        create = False
        if self.disabled_or_enabled:
            if self.simulation_mode and self.simulator is None:
                controller = self.active_controller
                self.simulator = mock_server.MockServer(controller.electrometer_type, False)
                await self.simulator.start_task
                controller.commander.hostname = self.simulator.host
                controller.commander.port = self.simulator.port
            if self.simulation_mode == 2:
                do_mock = True
                create = True
            if self.bucket is None:
                try:
                    controller = self.active_controller
                    self.bucket = salobj.AsyncS3Bucket(
                        salobj.AsyncS3Bucket.make_bucket_name(s3instance=controller.s3_instance),
                        create=create,
                        domock=do_mock,
                    )
                except Exception:
                    self.log.exception("Bucket creation failed.")
                    await self.fault(code=enums.Error.BUCKET, report="Bucket creation failed.")
                    return
            controller = self.active_controller
            if not controller.connected:
                try:
                    await controller.connect()
                except Exception:
                    self.log.exception("Connection failed.")
                    await self.fault(code=enums.Error.CONNECTION, report="Connection failed.")
                    return
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
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
            controller = self.active_controller
            await controller.perform_zero_calibration(
                mode=None, auto=None, set_range=None, integration_time=None
            )
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
            self.log.exception("performZeroCalibration failed.")
            raise
        finally:
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
            controller = self.active_controller
            await controller.set_digital_filter(
                activate_filter=data.activateFilter,
                activate_avg_filter=data.activateAvgFilter,
                activate_med_filter=data.activateMedFilter,
            )
            self.log.debug("setDigitalFilter controller interaction completed")
            self.log.debug(
                f"filter_active={controller.filter_active},"
                f"avg_filter_active={controller.avg_filter_active},"
                f"median_filter_active={controller.median_filter_active}"
            )
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
            self.log.exception("setDigitalFilter failed.")
            raise
        finally:
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
            controller = self.active_controller
            await controller.set_integration_time(data.intTime)
        except Exception:
            self.log.exception("setIntegrationTime failed.")
            raise
        finally:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_changeNPLC(self, data):
        """Change the Number of Power Line Cycles (NPLC).

        Parameters
        ----------
        data : `cmd_changeNPLC.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="changeNPLC")
        try:
            controller = self.active_controller
            await controller.set_timer(data.value)
        except Exception:
            self.log.exception("Failed to change NPLC.")
            raise
        finally:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_setMode(self, data):
        """Set the mode/unit.

        Parameters
        ----------
        data : `cmd_setMode.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="setMode")
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            controller = self.active_controller
            self.log.debug(f"Setting mode: {data.mode}")
            await controller.set_mode(mode=data.mode)
        except Exception:
            self.log.exception("setMode failed.")
            raise
        finally:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_setRange(self, data):
        """Set the range.

        Parameters
        ----------
        data : `cmd_setRange.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="setRange")
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            controller = self.active_controller
            await controller.set_range(set_range=data.setRange)
        except Exception:
            self.log.exception("setRange failed.")
            raise
        finally:
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
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="startScan")
        try:
            await self.report_detailed_state(DetailedState.MANUALREADINGSTATE)
            controller = self.active_controller
            await controller.start_scan(group_id=getattr(data, "groupId", None))
        except Exception as e:
            msg = "startScan failed."
            await self.fault(code=enums.Error.FILE_ERROR, report=f"{msg}: {repr(e)}")
        finally:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_startScanDt(self, data):
        """Start the scan with a set duration.

        Parameters
        ----------
        data : `cmd_startScanDt.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="startScanDt")
        try:
            await self.report_detailed_state(DetailedState.SETDURATIONREADINGSTATE)
            controller = self.active_controller
            await self.cmd_startScanDt.ack_in_progress(
                data=data,
                timeout=data.scanDuration,
                result="Starting scan on controller.",
            )
            await controller.start_scan_dt(
                scan_duration=data.scanDuration, group_id=getattr(data, "groupId", None)
            )
            await self.report_detailed_state(DetailedState.READINGBUFFERSTATE)
            await self.cmd_startScanDt.ack_in_progress(
                data=data,
                timeout=READ_DURATION,
                result="Reading the buffer from controller.",
            )
            scan_result = await controller.stop_scan()
            await self.write_scan_result(scan_result)
        except Exception as e:
            msg = "startScanDt failed."
            self.log.exception(msg)
            await self.fault(code=enums.Error.FILE_ERROR, report=f"{msg}: {repr(e)}")
        finally:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

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
            controller = self.active_controller
            scan_result = await controller.stop_scan()
            await self.write_scan_result(scan_result)
        except Exception as e:
            msg = "stopScan failed."
            self.log.exception(msg)
            await self.fault(code=enums.Error.FILE_ERROR, report=f"{msg}: {repr(e)}")
        finally:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

    async def do_setVoltageSource(self, data):
        """Set voltage source settings.

        Parameters
        ----------
        data : `cmd_setVoltageSource.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="setRange")
        try:
            await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
            controller = self.active_controller
            await controller.toggle_voltage_source(data.status)
            await controller.set_voltage_limit(data.voltage_limit)
            await controller.set_voltage_range(data.range)
            await controller.set_voltage_level(data.level)
        except Exception:
            self.log.exception("SetVoltageSource failed.")
            raise
        finally:
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
