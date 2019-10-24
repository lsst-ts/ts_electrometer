from lsst.ts import salobj
import enum
import pathlib


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

    async def do_performZeroCalib(self, id_data):
        pass

    async def do_setDigitalFilter(self, id_data):
        pass

    async def do_setIntegrationTime(self, id_data):
        pass

    async def do_setMode(self, id_data):
        pass

    async def do_setRange(self, id_data):
        pass

    async def do_startScan(self, id_data):
        pass

    async def do_startScanDt(self, id_data):
        pass

    async def do_stopScan(self, id_data):
        pass

    @staticmethod
    def get_config_pkg():
        pass
