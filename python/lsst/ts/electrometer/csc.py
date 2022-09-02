from lsst.ts import salobj, utils
from lsst.ts.idl.enums.Electrometer import DetailedState

from . import __version__
from . import controller, mock_server
from .config_schema import CONFIG_SCHEMA


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
    """

    valid_simulation_modes = (0, 1)
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
        self.controller = controller.ElectrometerController(csc=self, log=self.log)
        self.simulator = None
        self.run_event_loop = False
        self.event_loop_task = utils.make_done_future()
        self.default_force_output = True

    def assert_substate(self, substates, action):
        """Assert the CSC is in the proper substate.

        Parameters
        ----------
        substates
        action

        Raises
        ------
        salobj.ExpectedError
            If the current substate is not allowed to preform the action.
        """
        if self.detailed_state not in [
            DetailedState(substate) for substate in substates
        ]:
            raise salobj.ExpectedError(
                f"{action} not allowed in {self.detailed_state!r}"
            )

    @property
    def detailed_state(self):
        """The current substate of the CSC.

        Parameters
        ----------
        new_state : int
            The number of the new substate.

        Returns
        -------
        detailed_state : `lsst.ts.idl.enums.Electrometer.DetailedState`
            The sub state of the CSC.
        """
        return self.evt_detailedState.data.detailedState

    async def report_detailed_state(self, new_state):
        """Report the new detailed state."""
        detailed_state = DetailedState(new_state)
        await self.evt_detailedState.set_write(detailedState=detailed_state)

    async def configure(self, config):
        """Configure the Electrometer CSC.

        Parameters
        ----------
        config : types.SimpleNamespace
            The parsed yaml object.
        """
        self.controller.configure(config)

    async def handle_summary_state(self):
        if self.disabled_or_enabled:
            if self.simulation_mode and self.simulator is None:
                self.simulator = mock_server.MockServer()
                await self.simulator.start_task
            if not self.controller.connected:
                await self.controller.connect()
                await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        else:
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
        await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
        await self.controller.perform_zero_calibration()
        await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        self.log.info("Zero Calibration Completed")

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
        await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
        await self.controller.set_digital_filter(
            activate_filter=data.activateFilter,
            activate_avg_filter=data.activateAvgFilter,
            activate_med_filter=data.activateMedFilter,
        )
        self.log.debug("setDigitalFilter controller interaction completed")
        self.log.debug(f"filter_active={self.controller.filter_active}")
        self.log.debug(f"avg_filter_active={self.controller.avg_filter_active}")
        self.log.debug(f"median_filter_active={self.controller.median_filter_active}")
        await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        self.log.info("setDigitalFilter Completed")

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
        await self.report_detailed_state(DetailedState.CONFIGURINGSTATE)
        await self.controller.set_integration_time(int_time=data.intTime)
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
            await self.controller.set_mode(mode=data.mode)
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
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
            await self.controller.start_scan()
            await self.report_detailed_state(DetailedState.MANUALREADINGSTATE)
            self.log.debug("startScan Completed")
        except Exception:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)

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
            await self.controller.start_scan_dt(scan_duration=data.scanDuration)
            await self.report_detailed_state(DetailedState.READINGBUFFERSTATE)
            await self.controller.stop_scan()
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
        except Exception:
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
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
            await self.controller.stop_scan()
            await self.report_detailed_state(DetailedState.NOTREADINGSTATE)
            self.log.info("stopScan Completed")
        except Exception:
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
        await super().close_tasks()
        await self.controller.disconnect()
        if self.simulator is not None:
            await self.simulator.close()
            self.simulator = None
