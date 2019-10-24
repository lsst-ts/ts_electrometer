import enum

class UnitMode(enum.IntEnum):
    CURR = 1
    CHAR = 2
    VOLT = 3
    RES = 4

class Filter(enum.IntEnum):
    MED = 1
    AVER = 2

class AverFilterType(enum.IntEnum):
    NONE = 1
    SCAL = 2
    ADV = 3

class readingOption(enum.IntEnum):
    LATEST = 1
    NEWREAD = 2

class ElectrometerController:
    def __init__(self):
        self.commands = None
        self.mode = None
        self.range = None
        self.integration_time = 0.01
        self.median_filter_active = False
        self.filter_active = False
        self.avg_filter_active = False
        self.connected = False
        self.last_value = 0
        self.read_freq = 0.01
        self.stop_reading_value = False
        self.configuration_delay = 0.1
        self.start_and_end_scan_values = [[0,0],[0,0]]
        self.auto_range = False


class ElectrometerSimulator:
    def __init__(self):
        pass
