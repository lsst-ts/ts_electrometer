import pathlib

from lsst.ts import salobj
from lsst.ts.idl.enums import Electrometer

from . import controller


class ElectrometerCsc(salobj.ConfigurableCsc):
    """Class that implements the CSC for the electrometer.

    Parameters
    ----------
    index : int
        The index of the CSC.
    config_dir : str
        Path to config directory.
        One is provided for you in another method.
    initial_state : salobj.State
        The initial state of the CSC.
        Should be used for unit tests and development.
    initial_simulation_mode : int
        The simulation mode of the CSC.

    Attributes
    ----------
    controller : controller.ElectrometerController
        The controller object for the electrometer.
    run_event_loop : bool
        Whether the event loop runs.
    event_loop_task : asyncio.Task
        A task for handling the event loop.
        Currently not implemented.
    """
    def __init__(self, index, config_dir=None,
                 initial_state=salobj.State.STANDBY, initial_simulation_mode=0):
        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "Electrometer.yaml")
        super().__init__(name="Electrometer", index=index, schema_path=schema_path,
                         config_dir=config_dir, initial_state=initial_state,
                         initial_simulation_mode=initial_simulation_mode)
        self.controller = controller.ElectrometerController()
        self.run_event_loop = False
        self.event_loop_task = None

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
        if self.detailed_state not in [Electrometer.DetailedState(substate) for substate in substates]:
            raise salobj.ExpectedError(f"{action} not allowed in {self.detailed_state!r}")

    @property
    def detailed_state(self):
        """The current substate of the CSC.

        Parameters
        ----------
        new_state : int
            The number of the new substate.

        Returns
        -------
        detailed_state : Electrometer.DetailedState
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

    async def end_enable(self, id_data):
        """Connect the electrometer and configure to the settings specified.

        Parameters
        ----------
        id_data : data
            The data for the hook.
        """
        await self.controller.connect()
        self.evt_measureType.set_put(mode=self.controller.mode.value)
        self.evt_digitalFilterChange.set_put(activateFilter=self.controller.filter_active,
                                             activateAverageFilter=self.controller.avg_filter_active,
                                             activateMedianFilter=self.controller.median_filter_active)
        self.evt_integrationTime.set_put(intTime=self.controller.integration_time)
        self.evt_measureRange.set_put(rangeValue=self.controller.range)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def end_disable(self, id_data):
        """Disconnect the electrometer.

        Parameters
        ----------
        id_data : data
            The data for the hook.
        """
        self.controller.disconnect()

    async def do_performZeroCalib(self, id_data):
        """Perform zero calibration.

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("performZeroCalib")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE],
                             action="performZeroCalib")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.perform_zero_calibration()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setDigitalFilter(self, id_data):
        """Set the digital filter(s).

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("setDigitalFilter")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE],
                             action="setDigitalFilter")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        self.controller.set_digital_filter(activate_filter=id_data.activate_filter,
                                           activate_avg_filter=id_data.activate_avg_filter,
                                           activate_med_filter=id_data.activate_med_filter)
        self.evt_digitalFilterChange.set_put(activateFilter=self.controller.filter_active,
                                             activateAvgFilter=self.controller.avg_filter_active,
                                             activateMedFilter=self.controller.med_filter_active)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setIntegrationTime(self, id_data):
        """Set the integration time.

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("setIntegrationTime")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE],
                             action="setIntegrationTime")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.set_integration_time(int_time=id_data.int_time)
        self.evt_integrationTime.set_put(intTime=self.controller.integration_time)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setMode(self, id_data):
        """Set the mode/unit.

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("setMode")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="setMode")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.set_mode(mode=id_data.mode)
        await self.controller.get_mode()
        self.evt_measureType.set_put(mode=self.controller.mode.value)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setRange(self, id_data):
        """Set the range.

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("setRange")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="setRange")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        await self.controller.set_range(set_range=id_data.set_range)
        self.evt_measureRange.set_put(rangeValue=self.controller.range)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_startScan(self, id_data):
        """Start scan.

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("startScan")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="startScan")
        await self.controller.start_scan()
        self.detailed_state = Electrometer.DetailedState.MANUALREADINGSTATE

    async def do_startScanDt(self, id_data):
        """Start the scan with a set duration.

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("startScanDt")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="startScanDt")
        self.detailed_state = Electrometer.DetailedState.SETDURATIONREADINGSTATE
        await self.controller.start_scan_dt(scan_duration=id_data.scanDuration)
        self.detailed_state = Electrometer.DetailedState.READINGBUFFERSTATE
        await self.controller.stop_scan()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_stopScan(self, id_data):
        """Stop the scan.

        Parameters
        ----------
        id_data : data
            The data for the command.
        """
        self.assert_enabled("stopScan")
        self.assert_substate(substates=[Electrometer.DetailedState.MANUALREADINGSTATE,
                                        Electrometer.DetailedState.SETDURATIONREADINGSTATE],
                             action="stopScan")
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
