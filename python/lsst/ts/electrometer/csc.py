from lsst.ts import salobj
from lsst.ts.idl.enums import Electrometer

from . import __version__
from . import controller
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
        self.controller = controller.ElectrometerController(simulation_mode, log=self.log)
        self.run_event_loop = False
        self.event_loop_task = salobj.make_done_future()
        self._detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

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
            Electrometer.DetailedState(substate) for substate in substates
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
        return self._detailed_state

    @detailed_state.setter
    def detailed_state(self, new_state):
        self._detailed_state = Electrometer.DetailedState(new_state)
        self.report_detailed_state()

    def report_detailed_state(self):
        """Report the new detailed state."""
        self.evt_detailedState.set_put(detailedState=self.detailed_state)

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
            if not self.controller.connected:
                await self.controller.connect()
                self.evt_measureType.set_put(
                    mode=self.controller.mode.value, force_output=True
                )
                self.evt_digitalFilterChange.set_put(
                    activateFilter=self.controller.filter_active,
                    activateAverageFilter=self.controller.avg_filter_active,
                    activateMedianFilter=self.controller.median_filter_active,
                    force_output=True,
                )
                self.evt_integrationTime.set_put(
                    intTime=self.controller.integration_time, force_output=True
                )
                self.evt_measureRange.set_put(
                    rangeValue=self.controller.range, force_output=True
                )
                self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE
        else:
            if self.controller.connected:
                self.controller.disconnect()

    async def do_performZeroCalib(self, data):
        """Perform zero calibration.

        Parameters
        ----------
        data : `cmd_performZeroCalib.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[Electrometer.DetailedState.NOTREADINGSTATE],
            action="performZeroCalib",
        )
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.perform_zero_calibration()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE
        self.log.info("Zero Calibration Completed")

    async def do_setDigitalFilter(self, data):
        """Set the digital filter(s).

        Parameters
        ----------
        data : `cmd_setDigitalFilter.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[Electrometer.DetailedState.NOTREADINGSTATE],
            action="setDigitalFilter",
        )
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.set_digital_filter(
            activate_filter=data.activateFilter,
            activate_avg_filter=data.activateAvgFilter,
            activate_med_filter=data.activateMedFilter,
        )
        self.evt_digitalFilterChange.set_put(
            activateFilter=self.controller.filter_active,
            activateAverageFilter=self.controller.avg_filter_active,
            activateMedianFilter=self.controller.median_filter_active,
        )
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setIntegrationTime(self, data):
        """Set the integration time.

        Parameters
        ----------
        data : `cmd_setIntegrationTime.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[Electrometer.DetailedState.NOTREADINGSTATE],
            action="setIntegrationTime",
        )
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.set_integration_time(int_time=data.intTime)
        self.evt_integrationTime.set_put(
            intTime=self.controller.integration_time, force_output=True
        )
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setMode(self, data):
        """Set the mode/unit.

        Parameters
        ----------
        data : `cmd_setMode.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="setMode"
        )
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.set_mode(mode=data.mode)
        await self.controller.get_mode()
        self.evt_measureType.set_put(mode=self.controller.mode.value)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setRange(self, data):
        """Set the range.

        Parameters
        ----------
        data : `cmd_setRange.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="setRange"
        )
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.set_range(set_range=data.setRange)
        self.evt_measureRange.set_put(rangeValue=self.controller.range)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_startScan(self, data):
        """Start scan.

        Parameters
        ----------
        data : `cmd_startScan.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="startScan"
        )
        await self.controller.start_scan()
        self.detailed_state = Electrometer.DetailedState.MANUALREADINGSTATE

    async def do_startScanDt(self, data):
        """Start the scan with a set duration.

        Parameters
        ----------
        data : `cmd_startScanDt.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="startScanDt"
        )
        self.detailed_state = Electrometer.DetailedState.SETDURATIONREADINGSTATE
        await self.controller.start_scan_dt(scan_duration=data.scanDuration)
        self.detailed_state = Electrometer.DetailedState.READINGBUFFERSTATE
        await self.controller.stop_scan()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_stopScan(self, data):
        """Stop the scan.

        Parameters
        ----------
        data : `cmd_stopScan.DataType`
            The data for the command.
        """
        self.assert_enabled()
        self.assert_substate(
            substates=[
                Electrometer.DetailedState.MANUALREADINGSTATE,
                Electrometer.DetailedState.SETDURATIONREADINGSTATE,
            ],
            action="stopScan",
        )
        self.detailed_state = Electrometer.DetailedState.READINGBUFFERSTATE
        await self.controller.stop_scan()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    @staticmethod
    def get_config_pkg():
        """Get the config package.

        Returns
        -------
        str
            The name of the package where the configuration is stored.
        """
        return "ts_config_ocs"
