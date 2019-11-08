from lsst.ts import salobj
from lsst.ts.idl.enums import Electrometer
import pathlib
from . import model


class ElectrometerCsc(salobj.ConfigurableCsc):
    def __init__(self, index, config_dir=None,
                 initial_state=salobj.State.STANDBY, initial_simulation_mode=0):
        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "Electrometer.yaml")
        super().__init__(name="Electrometer", index=index, schema_path=schema_path,
                         config_dir=config_dir, initial_state=initial_state,
                         initial_simulation_mode=initial_simulation_mode)
        self.model = model.ElectrometerModel()

    def assert_substate(self, substates, action):
        if self.detailed_state not in [Electrometer.DetailedState(substate) for substate in substates]:
            raise salobj.ExpectedError(f"{action} not allowed in {self.detailed_state!r}")

    @property
    def detailed_state(self):
        return self._detailed_state

    @detailed_state.setter
    def detailed_state(self, new_state):
        self._detailed_state = Electrometer.DetailedState(new_state)
        self.report_detailed_state()

    def report_detailed_state(self):
        self.evt_detailedState.set_put(detailedState=self.detailed_state)

    async def configure(self, config):
        self.model.configure(config)

    async def implement_simulation_mode(self, mode):
        self.model.implement_simulation_mode(simulation_mode=mode)

    async def end_enable(self, id_data):
        self.model.connect()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def begin_disable(self, id_data):
        self.model.disconnect()

    async def do_performZeroCalib(self, id_data):
        self.assert_enabled("performZeroCalib")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE],
                             action="performZeroCalib")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        self.model.perform_zero_calib()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setDigitalFilter(self, id_data):
        self.assert_enabled("setDigitalFilter")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE],
                             action="setDigitalFilter")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        self.model.set_digital_filter(activate_filter=id_data.activate_filter,
                                      activate_avg_filter=id_data.activate_avg_filter,
                                      activate_med_filter=id_data.activate_med_filter)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setIntegrationTime(self, id_data):
        self.assert_enabled("setIntegrationTime")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE],
                             action="setIntegrationTime")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        self.model.set_integration_time(int_time=id_data.int_time)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setMode(self, id_data):
        self.assert_enabled("setMode")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="setMode")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        self.model.set_mode(mode=id_data.mode)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_setRange(self, id_data):
        self.assert_enabled("setRange")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="setRange")
        self.detailed_state = Electrometer.DetailedState.CONFIGURINGSTATE
        self.model.set_range(set_range=id_data.set_range)
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_startScan(self, id_data):
        print("csc start scan")
        self.assert_enabled("startScan")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="startScan")
        await self.model.start_scan()
        self.detailed_state = Electrometer.DetailedState.MANUALREADINGSTATE

    async def do_startScanDt(self, id_data):
        self.assert_enabled("startScanDt")
        self.assert_substate(substates=[Electrometer.DetailedState.NOTREADINGSTATE], action="startScanDt")
        self.detailed_state = Electrometer.DetailedState.SETDURATIONREADINGSTATE
        self.model.start_scan_dt(scan_duration=id_data.scan_duration)
        self.detailed_state = Electrometer.DetailedState.READINGBUFFERSTATE
        self.model.read_buffer()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    async def do_stopScan(self, id_data):
        self.assert_enabled("stopScan")
        self.assert_substate(substates=[Electrometer.DetailedState.MANUALREADINGSTATE,
                                        Electrometer.DetailedState.SETDURATIONREADINGSTATE],
                             action="stopScan")
        self.detailed_state = Electrometer.DetailedState.READINGBUFFERSTATE
        self.model.read_buffer()
        self.detailed_state = Electrometer.DetailedState.NOTREADINGSTATE

    @staticmethod
    def get_config_pkg():
        return "ts_config_ocs"
