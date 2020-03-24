from . import controller


class ElectrometerModel:
    def __init__(self):
        self.controller = None

    def configure(self, config):
        self.controller.configure(config=config)

    def perform_zero_calib(self):
        self.controller.perform_zero_calib()

    def set_digital_filter(self, activate_filter, activate_avg_filter, activate_med_filter):
        self.controller.filter_active = activate_filter
        self.controller.avg_filter_active = activate_avg_filter
        self.controller.median_filter_active = activate_med_filter

    def set_integration_time(self, int_time):
        self.controller.integration_time = int_time

    def set_mode(self, mode):
        self.controller.mode = mode

    def set_range(self, set_range):
        self.controller.range = set_range

    async def start_scan(self):
        await self.controller.start_scan()

    def start_scan_dt(self, scan_duration):
        self.controller.start_scan_dt(scan_duration=scan_duration)

    def stop_scan(self):
        self.controller.stop_scan()

    def connect(self):
        self.controller.connect()

    def disconnect(self):
        self.controller.disconnect()

    def implement_simulation_mode(self, simulation_mode):
        if simulation_mode == 0:
            self.controller = controller.ElectrometerController()
        elif simulation_mode == 1:
            self.controller = controller.ElectrometerSimulator()

    def read_buffer(self):
        self.controller.read_buffer()
