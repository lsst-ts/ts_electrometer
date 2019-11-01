import enum
import queue
import collections
import asyncio
import time
import pathlib
import datetime

import astropy.io.fits
import numpy as np


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
        self.start_and_end_scan_values = [[0, 0], [0, 0]]
        self.auto_range = False


class ElectrometerSimulator:
    def __init__(self):
        self.mode = UnitMode.CURR
        self.range = 0.1
        self.integration_time = 0.01
        self.median_filter_active = False
        self.filter_active = False
        self.avg_filter_active = False
        self.buffer = queue.Queue(maxsize=50000)
        self.error_codes = queue.Queue(maxsize=100)
        self.connected = False
        self.last_value = 0
        self.read_freq = 0.01
        self.stop_reading_value = False
        self.configuration_delay = 0.1
        self.start_and_end_scan_values = [[0, 0], [0, 0]]
        self.auto_range = False
        self.fits_file_directory = None
        self.value = collections.namedtuple('Value', ['intensity', 'time', 'temperature', 'unit'])

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, new_mode):
        self._mode = UnitMode(new_mode)

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, new_range):
        if new_range < 0:
            self.auto_range = True
        else:
            self.auto_range = False
        self._range = new_range

    @property
    def integration_time(self):
        return self._integration_time

    @integration_time.setter
    def integration_time(self, new_integration_time):
        self._integration_time = new_integration_time

    @property
    def median_filter_active(self):
        return self._median_filter_active

    @median_filter_active.setter
    def median_filter_active(self, activate_filter):
        self._median_filter_active = bool(activate_filter)

    @property
    def filter_active(self):
        return self._filter_active

    @filter_active.setter
    def filter_active(self, activate_filter):
        self._filter_active = bool(activate_filter)

    @property
    def avg_filter_active(self):
        return self._avg_filter_active

    @avg_filter_active.setter
    def avg_filter_active(self, activate_filter):
        self._avg_filter_active = bool(activate_filter)

    def configure(self, config):
        self.mode = config.mode
        self.range = config.range
        self.integration_time = config.integration_time
        self.median_filter_active = config.median_filter_active
        self.filter_active = config.filter_active
        self.avg_filter_active = config.avg_filter_active
        self.fits_file_directory = pathlib.Path(config.fits_files_path)
        self.fits_file_directory = self.fits_file_directory.expanduser()
        self.fits_file_directory.mkdir(parents=True, exist_ok=True)

    def perform_zero_calib(self):
        pass

    def set_digital_filter(self, activate_filter, activate_avg_filter, activate_median_filter):
        self.filter_active = bool(activate_filter)
        self.avg_filter_active = bool(activate_avg_filter)
        self.median_filter_active = bool(activate_median_filter)

    def set_integration_time(self, integration_time):
        self.integration_time = integration_time

    def set_mode(self, mode):
        self.mode = UnitMode(mode)

    def set_range(self, set_range):
        self.range = set_range

    async def start_scan(self):
        while not self.stop_reading_value:
            self.buffer.put(self.value(intensity=0, time=0, temperature=0, unit=self.mode.name))
            print(f"{self.buffer}")
            await asyncio.sleep(self.integration_time)

    async def start_scan_dt(self, scan_duration):
        start = time.time()
        dt = 0
        while not self.stop_reading_value or dt < scan_duration:
            dt = time.time() - start
            self.buffer.put(self.value(intensity=0, time=0, temperature=0, unit=self.mode.name))
            await asyncio.sleep(self.integration_time)

    def stop_scan(self):
        self.stop_reading_value = True

    def connect(self):
        # no need to do anything besides set flag
        self.connected = True

    def disconnect(self):
        # simulator doesn't actually do any port adjustment
        self.connected = False

    def read_buffer(self):
        # call create_fits_file since that's what should happen when we read
        # the buffer
        self.create_fits_file()

    def create_fits_file(self):
        # make ingrediants for fits file using PrimaryHDU
        # get info stored in buffer, use join to prevent race condition
        # make two lists with time and intensity
        # create array of two columns and set data to that value
        # use writeto helper function to create fits file
        times = []
        intensities = []
        filename = f"electrometer_{datetime.datetime.now(datetime.timezone.utc).timestamp()}.fits"
        hdu = astropy.io.fits.PrimaryHDU()
        hdu.header['CLMN1'] = ("Time", "Time in Seconds")
        hdu.header['CLMN2'] = ("Intensity", "")
        while self.buffer.join():
            scan = self.buffer.get()
            times.append(scan.time)
            intensities.append(scan.intensity)
        hdu.data = np.array([times, intensities])
        fits_file_path = pathlib.Path(f'{self.fits_file_directory}/{filename}')
        hdu.writeto(fits_file_path)
