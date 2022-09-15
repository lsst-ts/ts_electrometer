import asyncio
import logging
import re
import types

import astropy.io.fits as fits
import numpy as np
from lsst.ts import utils

from . import commander, commands_factory, enums


class ElectrometerController:
    """Class that provides high level control for electrometer.

    Parameters
    ----------
    simulation_mode : `int`
        Is the electrometer in simulation mode?

    Attributes
    ----------
    commander : `serial.Serial`
        The serial interface for writing and reading from the device.
    commands : `ElectrometerCommandFactory`
        The interface for providing formatted commands for the commander.
    mode : `UnitMode`
        The mode/unit of the electrometer.
    range : `float`
        The range of intensities that the electrometer can read.
    integration_time : `float`
        The amount of time the electrometer reads per scan.
    median_filter_active : `bool`
        Whether the median filter is active.
    filter_active : `bool`
        Whether any filter is active.
    avg_filter_active : `bool`
        Whether the average filter is active.
    connected : `bool`
        Whether the port is open.
    last_value : `int`
        The last value of the electrometer intensity read.
    read_freq : `float`
        The frequency that readings are gotten from the device buffer.
    configuration_delay : `float`
        The delay to allow the electrometer to configure.
    auto_range : `bool`
        Whether automatic range is active.
    manual_start_time : `float`
        The start TAI time of a scan [s].
    manual_end_time : `float`
        The end TAI time of a scan [s].
    serial_lock : `asyncio.Lock`
        The lock for protecting the synchronous serial communication.

    """

    def __init__(self, csc, log=None):

        # Create a logger if none were passed during the instantiation of
        # the class
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)

        self.csc = csc
        self.commander = commander.Commander(log=self.log)
        self.commands = commands_factory.ElectrometerCommandFactory()
        self.mode = None
        self.range = 0.1
        self.integration_time = 0.01
        self.median_filter_active = False
        self.filter_active = False
        self.avg_filter_active = False
        self.last_value = 0
        self.read_freq = 0.01
        self.configuration_delay = 0.1
        self.auto_range = False
        self.manual_start_time = None
        self.manual_end_time = None
        self.serial_lock = asyncio.Lock()
        self.modes = {
            1: enums.UnitMode.CURR,
            2: enums.UnitMode.CHAR,
            3: enums.UnitMode.VOLT,
            4: enums.UnitMode.RES,
        }

    @property
    def connected(self):
        return self.commander.connected

    def configure(self, config: types.SimpleNamespace) -> None:
        """Configure the controller.

        Parameters
        ----------
        config : `types.SimpleNamespace`
            The parsed yaml as a dict-like object.
        """
        self.mode = enums.UnitMode(self.modes[config.mode])
        self.range = config.range
        self.integration_time = config.integration_time
        self.median_filter_active = config.median_filter_active
        self.filter_active = config.filter_active
        self.avg_filter_active = config.avg_filter_active
        self.auto_range = True if self.range <= 0 else False
        self.commander.port = config.tcp_port
        self.commander.host = config.host
        self.commander.timeout = config.timeout
        self.file_output_dir = config.fits_files_path

    def generate_development_configure(self):
        """Generate a development config object.

        Used for development purposes to develop/test controller code.

        Returns
        -------
        config : `types.SimpleNamespace`
            A development configuration object.
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

    async def send_command(self, command: str, has_reply: bool = False):
        """Send a command to the device and return a reply if it has one.

        Parameters
        ----------
        command : `str`
            The message to be sent.
        has_reply : `bool`
            Whether the message has a reply.

        Returns
        -------
        reply : `str` or `None`
            If has_reply is True then returns string reply.
            If false, then returns None.
        """
        async with self.serial_lock:
            return await self.commander.send_command(msg=command, has_reply=has_reply)

    async def connect(self) -> None:
        """Open connection to the electrometer."""
        await self.commander.connect()

        # Send a message and verify the response to ensure connectivity
        res = await self.send_command(
            f"{self.commands.get_hardware_info()}", has_reply=True
        )
        expected = "KEITHLEY INSTRUMENTS INC."
        if expected not in res:
            self.log.error(
                f"Communication verification test failed."
                f"Expected:\n {expected} \n but got: \n{res} \n"
            )
            raise RuntimeError("Communication verification failed.")
        await self.set_mode(self.mode)
        await self.set_range(self.range)
        await self.set_integration_time(self.integration_time)
        await self.set_digital_filter(
            activate_filter=self.filter_active,
            activate_avg_filter=self.avg_filter_active,
            activate_med_filter=self.median_filter_active,
        )

    async def disconnect(self) -> None:
        """Close connection to the electrometer."""
        await self.commander.disconnect()

    async def perform_zero_calibration(self) -> None:
        """Perform zero calibration."""
        await self.send_command(
            f"{self.commands.perform_zero_calibration(self.mode,self.auto_range,self.range)}"
        )
        self.log.debug("Zero Calibration sent to controller")

    async def set_digital_filter(
        self,
        activate_filter: bool,
        activate_avg_filter: bool,
        activate_med_filter: bool,
    ):
        """Set the digital filter(s).

        Parameters
        ----------
        activate_filter : `bool`
            Whether any filter should be activated.
        activate_avg_filter : `bool`
            Whether the average filter should be activated.
        activate_med_filter : `bool`
            Whether the median filter should be activated.
        """
        filter_active = activate_avg_filter and activate_filter
        await self.send_command(
            f"{self.commands.activate_filter(self.mode, enums.Filter(2), filter_active)}"
        )
        filter_active = activate_med_filter and activate_filter
        await self.send_command(
            f"{self.commands.activate_filter(self.mode, enums.Filter(1), filter_active)}"
        )
        await self.csc.evt_digitalFilterChange.set_write(activateFilter=filter_active)
        await self.get_avg_filter_status()
        await self.get_med_filter_status()
        await self.check_error()

    async def set_integration_time(self, int_time):
        """Set the integration time.

        Parameters
        ----------
        int_time : `float`
            The integration time.
        """
        await self.send_command(
            f"{self.commands.integration_time(mode=self.mode, time=int_time)}"
        )
        await self.get_integration_time()
        await self.check_error()

    async def set_mode(self, mode):
        """Set the mode/unit.

        Parameters
        ----------
        mode : `int`
            The mode of the electrometer.
        """
        await self.send_command(f"{self.commands.set_mode(mode=mode)}")
        await self.get_mode()
        await self.check_error()

    async def set_range(self, set_range):
        """Set the range.

        Parameters
        ----------
        set_range : `float`
            The new range value.
        """
        await self.send_command(
            f"{self.commands.set_range(auto=self.auto_range, range_value=set_range, mode=self.mode)}"
        )
        await self.get_range()
        await self.check_error()

    async def start_scan(self):
        """Start storing values in the Keithley electrometer's buffer."""
        await self.send_command("TST:TYPE RTC;")
        await self.send_command(self.commands.set_timer(self.mode))
        await self.send_command(self.commands.enable_sync(False))
        await self.send_command(f"{self.commands.clear_buffer()}")
        await self.send_command(f"{self.commands.format_trac(timestamp=False)}")
        await self.send_command(f"{self.commands.set_buffer_size(50000)}")
        await self.send_command(
            f"{self.commands.select_source(source=enums.Source.IMM)}"
        )
        await self.send_command(f"{self.commands.enable_display(False)}")
        await self.send_command(f"{self.commands.next_read()}")
        self.manual_start_time = utils.current_tai()

    async def start_scan_dt(self, scan_duration):
        """Start storing values in the Keithley electrometer's buffer, for a
        set duration.

        Parameters
        ----------
        scan_duration : `float`
            The amount of time to store values for.
        """
        await self.send_command("TST:TYPE RTC;")
        await self.send_command(self.commands.set_timer(self.mode))
        await self.send_command(self.commands.enable_sync(False))
        await self.send_command(f"{self.commands.clear_buffer()}")
        await self.send_command(f"{self.commands.format_trac(timestamp=False)}")
        await self.send_command(f"{self.commands.set_buffer_size(50000)}")
        await self.send_command(
            f"{self.commands.select_source(source=enums.Source.IMM)}"
        )
        await self.send_command(f"{self.commands.enable_display(False)}")
        await self.send_command(f"{self.commands.next_read()}")
        self.manual_start_time = utils.current_tai()
        dt = 0
        while dt < scan_duration:
            await self.get_intensity()
            await self.csc.evt_intensity.set_write(intensity=self.last_value)
            await asyncio.sleep(self.integration_time)
            dt = utils.current_tai() - self.manual_start_time

    async def stop_scan(self):
        """Stop storing values in the Keithley electrometer."""
        self.manual_end_time = utils.current_tai()
        await self.send_command(f"{self.commands.stop_storing_buffer()}")
        await self.send_command(f"{self.commands.enable_display(True)}")
        self.log.debug("Scanning stopped, Now reading buffer.")
        res = await self.send_command(f"{self.commands.read_buffer()}", has_reply=True)
        intensity, times, temperature, unit = self.parse_buffer(res)
        self.write_fits_file(intensity, times, temperature, unit)

    def write_fits_file(self, intensity, times, temperature, unit):
        """Write fits file of the intensity, time, and temperature values.

        Parameters
        ----------
        intensity : `list`
            The intensity values
        times : `list`
            The time of the intensity value
        temperature : `list`
            The temperature of the intensity value
        unit : `list`
            The unit of the intensity value.
        """
        data = np.array([times, intensity])
        hdu = fits.PrimaryHDU(data)
        hdr = hdu.header
        hdr["CLMN1"] = ("Time", "Time in seconds")
        hdr["CLMN2"] = "Intensity"
        filename = f"{self.manual_start_time}_{self.manual_end_time}.fits"
        hdu.writeto(f"{self.file_output_dir}/{filename}")
        self.log.info(f"Electrometer Scan data file written: {filename}")
        self.log.info(
            f"Scan Summary of [Mean, median, std] is: "
            f"[{np.mean(intensity):0.5e}, {np.median(intensity):0.5e}, {np.std(intensity):0.5e}]"
        )

    def parse_buffer(self, response):
        """Parse the buffer values.

        Parameters
        ----------
        response : `str`
            The response from the read buffer command.

        Returns
        -------
        intensity : `list`
            The intensity values
        time : `list`
            The time values
        temperature : `list`
            The temperature values.
        unit : `list`
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
            if i >= len(unsorted_values) - 2:
                break

        return intensity, time, temperature, unit

    async def check_error(self):
        """Check the error."""
        res = await self.send_command(
            f"{self.commands.get_last_error()}", has_reply=True
        )
        self.error_code, self.message = res.split(",")

    async def get_mode(self):
        """Get the mode/unit."""
        res = await self.send_command(f"{self.commands.get_mode()}", has_reply=True)
        if res not in ['"CHAR"', '"RES"']:
            mode, unit = res.split(":")
            mode = mode.replace('"', "")
        else:
            mode = res
            mode = mode.replace('"', "")
        self.mode = enums.UnitMode(mode)
        await self.csc.evt_measureType.set_write(
            mode=list(self.modes.values()).index(self.mode), force_output=True
        )

    async def get_avg_filter_status(self):
        """Get the average filter status."""
        res = await self.send_command(
            f"{self.commands.get_filter_status(self.mode, 2)}", has_reply=True
        )
        self.log.debug(f"Average filter response is {res}")
        self.avg_filter_active = bool(int(res))
        await self.csc.evt_digitalFilterChange.set_write(
            activateAverageFilter=self.avg_filter_active
        )

    async def get_med_filter_status(self):
        """Get the median filter status."""
        res = await self.send_command(
            f"{self.commands.get_filter_status(self.mode, 1)}", has_reply=True
        )
        self.log.debug(f"median filter response is {res}")
        self.median_filter_active = bool(int(res))
        await self.csc.evt_digitalFilterChange.set_write(
            activateMedianFilter=self.median_filter_active
        )

    async def get_range(self):
        """Get the range value."""
        res = await self.send_command(
            f"{self.commands.get_range(self.mode)}", has_reply=True
        )
        self.range = float(res)
        await self.csc.evt_measureRange.set_write(
            rangeValue=self.range, force_output=True
        )

    async def get_integration_time(self):
        """Get the integration time value."""
        res = await self.send_command(
            f"{self.commands.get_integration_time(self.mode)}", has_reply=True
        )
        self.integration_time = float(res)
        await self.csc.evt_integrationTime.set_write(
            intTime=self.integration_time, force_output=True
        )

    async def get_intensity(self):
        """Get the intensity."""
        res = await self.send_command(f"{self.commands.get_measure(1)}", has_reply=True)
        res = res.split(",")
        res = res[0].strip("ZVDCNA")
        self.last_value = float(res)
