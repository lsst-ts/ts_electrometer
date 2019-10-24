from lsst.ts import salobj
import enum
import pathlib
from . import model


class DetailedState(enum.IntEnum):
    DISABLEDSTATE = 1
    ENABLEDSTATE = 2
    FAULTSTATE = 3
    OFFLINESTATE = 4
    STANDBYSTATE = 5
    NOTREADINGSTATE = 6
    CONFIGURINGSTATE = 7
    MANUALREADINGSTATE = 8
    READINGBUFFERSTATE = 9
    SETDURATIONREADINGSTATE = 10


class Units(enum.IntEnum):
    current = 1
    charge = 2


class ElectrometerCsc(salobj.ConfigurableCsc):
    def __init__(self, index, config_dir=None,
                 initial_state=salobj.State.STANDBY, initial_simulation_mode=0):
        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "Electrometer.yaml")
        super().__init__(name="Electrometer", index=index, schema_path=schema_path,
                         config_dir=config_dir, initial_state=initial_state,
                         initial_simulation_mode=initial_simulation_mode)
        self.model = model.ElectrometerModel()

    def assert_substate(self, substates, action):
        if self.detailed_state not in [DetailedState(substate) for substate in substates]:
            raise salobj.ExpectedError(f"{action} not allowed in {self.detailed_state!r}")

    @property
    def detailed_state(self):
        return self._detailed_state

    @detailed_state.setter
    def detailed_state(self, new_state):
        self._detailed_state = DetailedState(new_state)
        self.report_detailed_state()

    def report_detailed_state(self):
        self.evt_detailedState.set_put(detailedState=self.detailed_state)

    async def configure(self, config):
        pass

    async def end_enable(self, id_data):
        self.model.connect()
        self.detailed_state = DetailedState.NOTREADINGSTATE

    async def do_performZeroCalib(self, id_data):
        self.assert_enabled("performZeroCalib")
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="performZeroCalib")
        self.detailed_state = DetailedState.CONFIGURINGSTATE
        self.model.perform_zero_calib()
        self.detailed_state = DetailedState.NOTREADINGSTATE

    async def do_setDigitalFilter(self, id_data):
        self.assert_enabled("setDigitalFilter")
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="setDigitalFilter")
        self.detailed_state = DetailedState.CONFIGURINGSTATE
        self.model.set_digital_filter(activate_filter=id_data.activate_filter,
                                      activate_avg_filter=id_data.activate_avg_filter,
                                      activate_med_filter=id_data.activate_med_filter)
        self.detailed_state = DetailedState.NOTREADINGSTATE

    async def do_setIntegrationTime(self, id_data):
        self.assert_enabled("setIntegrationTime")
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="setIntegrationTime")
        self.detailed_state = DetailedState.CONFIGURINGSTATE
        self.model.set_integration_time(int_time=id_data.int_time)
        self.detailed_state = DetailedState.NOTREADINGSTATE

    async def do_setMode(self, id_data):
        self.assert_enabled("setMode")
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="setMode")
        self.detailed_state = DetailedState.CONFIGURINGSTATE
        self.model.set_mode(mode=id_data.mode)
        self.detailed_state = DetailedState.NOTREADINGSTATE

    async def do_setRange(self, id_data):
        self.assert_enabled("setRange")
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="setRange")
        self.detailed_state = DetailedState.CONFIGURINGSTATE
        self.model.set_range(set_range=id_data.set_range)
        self.detailed_state = DetailedState.NOTREADINGSTATE

    async def do_startScan(self, id_data):
        self.assert_enabled("startScan")
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="startScan")
        self.model.start_scan()
        self.detailed_state = DetailedState.MANUALREADINGSTATE

    async def do_startScanDt(self, id_data):
        self.assert_enabled("startScanDt")
        self.assert_substate(substates=[DetailedState.NOTREADINGSTATE], action="startScanDt")
        self.detailed_state = DetailedState.SETDURATIONREADINGSTATE
        self.model.start_scan_dt(scan_duration=id_data.scan_duration)
        self.detailed_state = DetailedState.READINGBUFFERSTATE
        self.model.read_buffer()
        self.detailed_state = DetailedState.NOTREADINGSTATE

    async def do_stopScan(self, id_data):
        self.assert_enabled("stopScan")
        self.assert_substate(substates=[DetailedState.MANUALREADINGSTATE,
                                        DetailedState.SETDURATIONREADINGSTATE], action="stopScan")
        self.detailed_state = DetailedState.READINGBUFFERSTATE
        self.model.read_buffer()
        self.detailed_state = DetailedState.NOTREADINGSTATE

    @staticmethod
    def get_config_pkg():
        return "ts_config_electrometer"
