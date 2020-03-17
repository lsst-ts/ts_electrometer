import asyncio
import collections
import datetime
import enum
import pathlib
import queue
import time
import re
from types import SimpleNamespace

import astropy.io.fits as fits
import numpy as np
import serial

from .commands import ElectrometerCommand


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
        self.commander = serial.Serial()
        self.commands = ElectrometerCommand()
        self.mode = None
        self.range = None
        self.integration_time = 0.01
        self.median_filter_active = False
        self.filter_active = False
        self.avg_filter_active = False
        self.connected = False
        self.last_value = 0
        self.read_freq = 0.01
        self.configuration_delay = 0.1
        self.auto_range = False
        self.manual_start_time = None
        self.manual_end_time = None

    def configure(self, config):
        self.mode = UnitMode(config.mode)
        self.range = config.range
        self.integration_time = config.integration_time
        self.median_filter_active = config.median_filter_active
        self.filter_active = config.filter_active
        self.avg_filter_active = config.avg_filter_active
        self.auto_range = True if self.range <= 0 else False
        self.commander.port = config.serial_port
        self.commander.baudrate = config.baudrate
        self.commander.timeout = config.timeout

    def develop_configure(self):
        config = SimpleNamespace()
        config.mode = 1
        config.range = -0.01
        config.integration_time = 0.01
        config.median_filter_active = False
        config.filter_active = True
        config.avg_filter_active = False
        config.serial_port = "/dev/electrometer"
        config.baudrate = 57600
        config.timeout = 3.3
        return config

    def connect(self):
        self.commander.open()
        self.connected = True
        # self.commander.write(self.commands.enable_display(False).encode())
        self.set_mode(self.mode)
        self.set_range(self.range)
        self.set_digital_filter(self.filter_active, self.avg_filter_active, self.median_filter_active)

    def disconnect(self):
        # self.commander.write(self.commands.enable_display(True).encode())
        self.commander.close()
        self.connected = False

    def perform_zero_calibration(self):
        self.commander.write(f"{self.commands.perform_zero_calibration(self.mode, self.auto_range, self.range)}\r".encode())

    def set_digital_filter(self, activate_filter, activate_avg_filter, activate_med_filter):
        filter = activate_filter
        if activate_avg_filter is True and activate_filter is False:
            filter = False
        if activate_avg_filter is False and activate_filter is True:
            filter = False
        self.commander.write(f"{self.commands.activate_filter(self.mode, Filter(2), filter)}\r".encode())
        filter = activate_filter
        if activate_med_filter is True and activate_filter is False:
            filter = False
        if activate_med_filter is False and activate_filter is True:
            filter = False
        self.commander.write(f"{self.commands.activate_filter(self.mode, Filter(1), filter)}\r".encode())
        self.check_error()

    def set_integration_time(self, int_time):
        self.commander.write(f"{self.commands.integration_time(mode=self.mode, time=int_time)}\r".encode())
        self.check_error()

    def set_mode(self, mode):
        self.commander.write(f"{self.commands.set_mode(mode=mode)}\r".encode())
        self.check_error()

    def set_range(self, set_range):
        self.commander.write(f"{self.commands.set_range(auto=self.auto_range, range_value=set_range, mode=self.mode)}\r".encode())
        self.check_error()

    def start_scan(self):
        self.commander.write(f"{self.commands.clear_buffer()}\r".encode())
        self.commander.write(f"{self.commands.format_trac()}\r".encode())
        self.commander.write(f"{self.commands.set_buffer_size(50000)}\r".encode())
        self.commander.write(f"{self.commands.select_device_timer()}\r".encode())
        self.commander.write(f"{self.commands.next_read()}\r".encode())
        self.manual_start_time = time.time()

    def start_scan_dt(self, scan_duration):
        self.commander.write(f"{self.commands.prepare_device_scan()}\r".encode())
        self.manual_start_time = time.time()
        dt = 0
        # FIXME blocking and needs to be non-blocking
        while dt < scan_duration:
            time.sleep(self.integration_time)
            dt = time.time() - self.manual_start_time

    def stop_scan(self):
        self.manual_end_time = time.time()
        self.commander.write(f"{self.commands.stop_storing_buffer()}\r".encode())
        self.commander.write(f"{self.commands.read_buffer()}\r".encode())
        res = self.commander.read_until(b"\n")
        intensity, times, temperature, unit = self.parse_buffer(res.decode())
        self.write_fits_file(intensity, times, temperature, unit)

    def write_fits_file(self, intensity, times, temperature, unit):
        data = np.array([times, intensity])
        hdu = fits.PrimaryHDU(data)
        hdr = hdu.header
        hdr['CLMN1'] = ("Time", "Time in seconds")
        hdr['CLMN2'] = ("Intensity")
        hdu.writeto(f'/home/saluser/{self.manual_start_time}_{self.manual_end_time}.fits')

    def parse_buffer(self, response):
        regex_numbers = "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"
        regex_strings = "(?!E+)[a-zA-Z]+"
        intensity, time, temperature, unit = [], [], [], []
        unsorted_values = list(map(float, re.findall(regex_numbers, response)))
        unsorted_str_values = re.findall(regex_strings, response)
        i = 0
        while i < 50000:
            intensity.append(unsorted_values[i])
            time.append(unsorted_values[i + 1])
            temperature.append(0)
            unit.append(unsorted_str_values[i])
            i += 3
            if(i >= len(unsorted_values) - 2):
                break

        return intensity, time, temperature, unit

    def check_error(self):
        self.commander.write(f"{self.commands.get_last_error()}\r".encode())
        res = self.commander.read_until(b"\n")
        self.error_code, self.message = res.decode().strip().split(",")

    def get_mode(self):
        self.commander.write(f"{self.commands.get_mode()}\r".encode())
        res = self.commander.read_until(b"\n")
        mode, unit = res.decode().strip().split(":")
        mode = mode.replace('"', '')
        self.mode = UnitMode(UnitMode[mode].value)

    def get_avg_filter_status(self):
        self.commander.write(f"{self.commands.get_filter_status(self.mode, 2)}\r".encode())
        res = self.commander.read_until(b"\n")
        self.avg_filter_active = bool(res.decode().strip())

    def get_med_filter_status(self):
        self.commander.write(f"{self.commands.get_filter_status(self.mode, 1)}\r".encode())
        res = self.commander.read_until(b"\n")
        self.median_filter_active = bool(res.decode().strip())

    def get_range(self):
        self.commander.write(f"{self.commands.get_range(self.mode)}\r".encode())
        res = self.commander.read_until(b"\n")
        self.range = float(res.decode().strip())

    def get_integration_time(self):
        self.commander.write(f"{self.commands.get_integration_time(self.mode)}\r".encode())
        res = self.commander.read_until(b"\n")
        self.integration_time = float(res.decode().strip())

