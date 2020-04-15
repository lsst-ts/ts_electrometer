import asyncio
import time
import re
import types

import astropy.io.fits as fits
import numpy as np
import serial

from . import commands_factory, enums


class ElectrometerController:
    """Class that provides high level control for electrometer.

    Attributes
    ----------
    commander : serial.Serial
        The serial interface for writing and reading from the device.
    commands : ElectrometerCommand
        The interface for providing formatted commands for the commander.
    mode : UnitMode
        The mode/unit of the electrometer.
    range : float
        The range of intensities that the electrometer can read.
    integration_time : float
        The amount of time the electrometer reads per scan.
    median_filter_active : bool
        Whether the median filter is active.
    filter_active : bool
        Whether any filter is active.
    avg_filter_active : bool
        Whether the average filter is active.
    connected : bool
        Whether the port is open.
    last_value : int
        The last value of the electrometer intensity read.
    read_freq : float
        The frequency that readings are gotten from the device buffer.
    configuration_delay : float
        The delay to allow the electrometer to configure.
    auto_range : bool
        Whether automatic range is active.
    manual_start_time : int
        The start time of a scan.
    manual_end_time : int
        The end time of a scan.
    serial_lock : asyncio.Lock
        The lock for protecting the synchronous serial communication.

    """
    def __init__(self):
        self.commander = serial.Serial()
        self.commands = commands_factory.ElectrometerCommandFactory()
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
        self.serial_lock = asyncio.Lock()
        self.connected = False

    def configure(self, config):
        """Configure the controller.

        Parameters
        ----------
        config : types.Namespace
            The parsed yaml as a dict-like object.
        """
        self.mode = enums.UnitMode(config.mode)
        self.range = config.range
        self.integration_time = config.integration_time
        self.median_filter_active = config.median_filter_active
        self.filter_active = config.filter_active
        self.avg_filter_active = config.avg_filter_active
        self.auto_range = True if self.range <= 0 else False
        self.commander.port = config.serial_port
        self.commander.baudrate = config.baudrate
        self.commander.timeout = config.timeout

    def generate_development_configure(self):
        """Generate a development config object.

        Used for development purposes to develop/test controller code.
        """
        config = types.SimpleNamespace()
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

    async def send_command(self, command, has_reply=False):
        """Send a command to the device and return a reply if it has one.

        Parameters
        ----------
        command : str
            The message to be sent.
        has_reply : bool
            Whether the message has a reply.

        Returns
        -------
        reply : str or None
            If has_reply is True then returns string reply.
            If false, then returns None.
        """
        async with self.serial_lock:
            self.commander.write(f"{command}\r".encode())
            if has_reply:
                reply = self.commander.read_until(b"\n")
                return reply.decode().strip()

    async def connect(self):
        """Open connection to the electrometer."""
        self.commander.open()
        self.connected = True
        # self.commander.write(self.commands.enable_display(False).encode())
        await self.set_mode(self.mode)
        await self.set_range(self.range)
        await self.set_digital_filter(self.filter_active, self.avg_filter_active, self.median_filter_active)

    def disconnect(self):
        """Close connection to the electrometer."""
        # self.commander.write(self.commands.enable_display(True).encode())
        self.commander.close()
        self.connected = False

    async def perform_zero_calibration(self):
        """Perform zero calibration."""
        await self.send_command(
            f"{self.commands.perform_zero_calibration(self.mode,self.auto_range,self.range)}")

    async def set_digital_filter(self, activate_filter, activate_avg_filter, activate_med_filter):
        """Set the digital filter(s).

        Parameters
        ----------
        activate_filter: bool
            Whether any filter should be activated.
        activate_avg_filter : bool
            Whether the average filter should be activated.
        activate_med_filter : bool
            Whether the median filter should be activated.
        """
        filter_active = activate_filter
        if activate_avg_filter is True and activate_filter is False:
            filter_active = False
        if activate_avg_filter is False and activate_filter is True:
            filter_active = False
        await self.send_command(f"{self.commands.activate_filter(self.mode, enums.Filter(2), filter_active)}")
        filter_active = activate_filter
        if activate_med_filter is True and activate_filter is False:
            filter_active = False
        if activate_med_filter is False and activate_filter is True:
            filter_active = False
        await self.send_command(f"{self.commands.activate_filter(self.mode, enums.Filter(1), filter_active)}")
        await self.check_error()

    async def set_integration_time(self, int_time):
        """Set the integration time.

        Parameters
        ----------
        int_time : float
            The integration time.
        """
        await self.send_command(f"{self.commands.integration_time(mode=self.mode, time=int_time)}")
        await self.check_error()

    async def set_mode(self, mode):
        """Set the mode/unit.

        Parameters
        ----------
        mode : int
            The mode of the electrometer.
        """
        await self.send_command(f"{self.commands.set_mode(mode=mode)}")
        await self.check_error()

    async def set_range(self, set_range):
        """Set the range.

        Parameters
        ----------
        set_range : float
            The new range value.
        """
        await self.send_command(
            f"{self.commands.set_range(auto=self.auto_range, range_value=set_range, mode=self.mode)}")
        await self.check_error()

    async def start_scan(self):
        """Start storing values to the buffer."""
        await self.send_command(f"{self.commands.clear_buffer()}")
        await self.send_command(f"{self.commands.format_trac()}")
        await self.send_command(f"{self.commands.set_buffer_size(50000)}")
        await self.send_command(f"{self.commands.select_device_timer()}")
        await self.send_command(f"{self.commands.next_read()}")
        self.manual_start_time = time.time()

    async def start_scan_dt(self, scan_duration):
        """Start storing values to the buffer for a set duration.

        Parameters
        ----------
        scan_duration : float
            The amount of time to store values for.
        """
        await self.send_command(f"{self.commands.prepare_device_scan()}")
        self.manual_start_time = time.time()
        dt = 0
        # FIXME blocking and needs to be non-blocking
        while dt < scan_duration:
            await asyncio.sleep(self.integration_time)
            dt = time.monotonic() - self.manual_start_time

    async def stop_scan(self):
        """Stop storing values to the buffer."""
        self.manual_end_time = time.time()
        await self.send_command(f"{self.commands.stop_storing_buffer()}")
        res = await self.send_command(f"{self.commands.read_buffer()}", has_reply=True)
        intensity, times, temperature, unit = self.parse_buffer(res)
        self.write_fits_file(intensity, times, temperature, unit)

    def write_fits_file(self, intensity, times, temperature, unit):
        """Write fits file given values from buffer.

        Parameters
        ----------
        intensity : list
            The intensity values
        times : list
            The time of the intensity value
        temperature : list
            The temperature of the intensity value
        unit : list
            The unit of the intensity value.
        """
        data = np.array([times, intensity])
        hdu = fits.PrimaryHDU(data)
        hdr = hdu.header
        hdr['CLMN1'] = ("Time", "Time in seconds")
        hdr['CLMN2'] = ("Intensity")
        hdu.writeto(f'/home/saluser/{self.manual_start_time}_{self.manual_end_time}.fits')

    def parse_buffer(self, response):
        """Parse the buffer values.

        Parameters
        ----------
        response : str
            The response from the read buffer command.

        Returns
        -------
        intensity : list
            The intensity values
        time : list
            The time values
        temperature : list
            The temperature values.
        unit : list
            The unit values.
        """
        regex_numbers = r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"
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

    async def check_error(self):
        """Check the error."""
        res = await self.send_command(f"{self.commands.get_last_error()}", has_reply=True)
        self.error_code, self.message = res.split(",")

    async def get_mode(self):
        """Get the mode/unit."""
        res = await self.send_command(f"{self.commands.get_mode()}", has_reply=True)
        mode, unit = res.split(":")
        mode = mode.replace('"', '')
        self.mode = enums.UnitMode(enums.UnitMode[mode].value)

    async def get_avg_filter_status(self):
        """Get the average filter status."""
        res = await self.send_command(f"{self.commands.get_filter_status(self.mode, 2)}", has_reply=True)
        self.avg_filter_active = bool(res)

    async def get_med_filter_status(self):
        """Get the median filter status."""
        res = await self.send_command(f"{self.commands.get_filter_status(self.mode, 1)}", has_reply=True)
        self.median_filter_active = bool(res)

    async def get_range(self):
        """Get the range value."""
        res = await self.send_command(f"{self.commands.get_range(self.mode)}", has_reply=True)
        self.range = float(res)

    async def get_integration_time(self):
        """Get the integration time value."""
        res = await self.send_command(f"{self.commands.get_integration_time(self.mode)}", has_reply=True)
        self.integration_time = float(res)
