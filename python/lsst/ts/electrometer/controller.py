# This file is part of ts_electrometer.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = [
    "ElectrometerController",
    "KeysightElectrometerController",
    "KeithleyElectrometerController",
]

import abc
import asyncio
import dataclasses
import io
import logging
import re
import types

import astropy.io.fits as fits
import yaml
from astropy import table

from lsst.ts import utils

from . import commander, commands_factory, enums

TIME_PER_LINE = 0.0047
"""The time per line is calculated based on the result that 200 samples takes
~4 seconds."""
OVERHEAD_FACTOR = 1.3
"""Assume a 30% overhead when gathering data from the buffer."""
SLEEP = 2
MAX_ERROR_DRAIN = 10
ERROR_DRAIN_TIMEOUT = 10
ZERO_CALIBRATION_DELAY = 2


@dataclasses.dataclass
class ScanResult:
    """Data collected during one electrometer scan.

    Parameters
    ----------
    data : `dict` [`str`, `list` [`float`]]
        Parsed scan samples keyed by data column name.
    trace_elements : `list` [`str`]
        Column names reported by the electrometer trace format.
    start_time : `float`
        Scan start time, TAI seconds.
    end_time : `float`
        Scan end time, TAI seconds.
    duration : `float`
        Scan duration, in seconds.
    group_id : `str` or `None`
        Optional observing group identifier associated with the scan.
    """

    data: dict[str, list[float]]
    trace_elements: list[str]
    start_time: float
    end_time: float
    duration: float
    group_id: str | None


class ElectrometerController(abc.ABC):
    """Provide high-level control for an electrometer.

    Parameters
    ----------
    log : `logging.Logger` or `None`, optional
        Logger for controller messages. If `None`, a logger named for the
        concrete controller class is created.

    Attributes
    ----------
    commander : `commander.Commander`
        The tcpip interface for writing and reading from the device.
    commands : `ElectrometerCommandFactory`
        The interface for providing formatted commands for the commander.
    mode : `str` or `None`
        The current measurement mode name.
    range : `float`
        The current measurement range.
    integration_time : `float`
        Integration time for one measurement, in seconds.
    median_filter_active : `bool`
        Whether the median filter is active.
    filter_active : `bool`
        Whether any filter is active.
    avg_filter_active : `bool`
        Whether the average filter is active.
    last_value : `int`
        The last intensity value read from the electrometer.
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
    modes : `dict`
        Associate SAL Command number with electrometer UnitMode enum.
    group_id : `str` or `None`
        Optional observing group identifier for the current scan.
    voltage_source : `bool`
        Whether the voltage source is enabled.
    voltage_range : `int`
        Voltage source range.
    voltage_limit : `int`
        Voltage source limit.
    voltage_level : `int`
        Voltage source level.
    temperature : `float` or `None`
        Temperature returned from the probe, in degrees C.
    vsource : `float` or `None`
        Voltage source input, in volts.
    """

    def __init__(self, log=None):
        # Create a logger if none were passed during the instantiation of
        # the class
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)

        self.mode = None
        self.range = 0.1
        self.integration_time = 0.01
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
        self.voltage_status = None
        self.temperature = None
        self.vsource = None
        self.commander = commander.Commander(log=self.log, brand=None)
        self.commands = commands_factory.ElectrometerCommandFactory()
        self.median_filter_active = False
        self.filter_active = False
        self.avg_filter_active = False
        self.group_id = None

    @property
    def connected(self):
        """Whether the TCP/IP client is connected."""
        return self.commander.connected

    def parse_buffer(self, response, num_categories=2):
        """Parse the buffer values.

        Parameters
        ----------
        response : `str`
            The response from the read buffer command.
        num_categories : `int`, optional
            Number of values in each sample.

        Returns
        -------
        categorized_lists : `list` [`list` [`float`]]
            Parsed values grouped by category.
        """
        regex_numbers = r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"
        # regex_strings = "(?!E+)[a-zA-Z]+"
        raw_values = list(map(float, re.findall(regex_numbers, response)))

        # Converting each value to a float
        raw_str_values = [float(value) for value in raw_values]

        # Creating separate lists for each category
        categorized_lists = [[] for _ in range(num_categories)]
        for i, value in enumerate(raw_str_values):
            category_index = i % num_categories
            categorized_lists[category_index].append(value)
        return categorized_lists

    @abc.abstractmethod
    def configure(self, config):
        """Configure the controller.

        Parameters
        ----------
        config : `types.SimpleNamespace`
            Configuration for one electrometer instance.
        """
        self.default = types.SimpleNamespace(
            mode=config.mode,
            range=config.range,
            filters=types.SimpleNamespace(**config.filters),
            integration_time=config.integration_time,
        )

        self.mode = self.modes[config.mode].name
        self.range = config.range
        self.integration_time = config.integration_time
        tcpip = types.SimpleNamespace(**config.tcpip)
        self.commander = commander.Commander(log=self.log, brand=config.electrometer_type)
        self.commander.configure(tcpip)
        self.s3_instance = config.s3_instance
        self.fits_file_path = config.fits_file_path
        self.image_name_service = config.image_name_service
        self.sensor = types.SimpleNamespace(**config.sensor)
        self.sensor_brand = self.sensor.brand
        self.sensor_model = self.sensor.model
        self.sensor_serial = self.sensor.serial_number
        self.accessories = types.SimpleNamespace(**config.accessories)
        self.location = config.location
        self.electrometer_type = config.electrometer_type
        self.model_id = config.electrometer_model
        self.image_service_client = None

    @classmethod
    @abc.abstractmethod
    def get_config_schema(cls):
        """Return the JSON schema for this controller configuration."""
        pass

    async def send_command(self, command, has_reply=False, timeout=None):
        """Send a command to the electrometer.

        Parameters
        ----------
        command : `str`
            Command string to send.
        has_reply : `bool`, optional
            Whether a reply is expected.
        timeout : `float` or `None`, optional
            Timeout for the command reply, in seconds.

        Returns
        -------
        reply : `str` or `None`
            Reply from the electrometer if ``has_reply`` is true; otherwise
            `None`.
        """
        return await self.commander.send_command(
            msg=command,
            has_reply=has_reply,
            timeout=timeout,
        )

    async def connect(self):
        """Connect to, identify, and initialize the electrometer."""
        await self.commander.connect()
        try:
            id = await self.send_command(command=self.commands.get_hardware_info(), has_reply=True)
        except Exception as e:
            raise TimeoutError("No ID received.") from e
        expected_type = self.electrometer_type
        match expected_type:
            case "Keithley":
                if "KEITHLEY" in id:
                    pass
                else:
                    raise RuntimeError("Electrometer did not report expected type.")
            case "Keysight":
                if "Keysight" in id:
                    pass
                else:
                    raise RuntimeError("Electrometer did not report expected type.")
            case _:
                raise RuntimeError("Expected type is not valid.")
        await self.send_command(command=self.commands.reset_device())
        await self.send_command(command=self.commands.clear())
        match expected_type:
            case "Keysight":
                await self.send_command(command=self.commands.output_trigger_line())
        self.log.debug("Device reset.")

        await self.set_mode(self.mode)
        await self.set_range(self.range)
        await self.set_timer(self.integration_time)

        await self.set_digital_filter(
            activate_filter=self.default.filters.general,
            activate_avg_filter=self.default.filters.average,
            activate_med_filter=self.default.filters.median,
        )

    async def disconnect(self):
        """Disconnect from the electrometer."""
        self.image_service_client = None
        await self.commander.disconnect()

    async def perform_zero_calibration(self, mode=None, auto=None, set_range=None, integration_time=None):
        """This enables the zero check and sets the mode and range before
        every measurement.

        Parameters
        ----------
        mode : `str` | None
            Mode of measurement, CURR, CHAR, VOLT, RES
        auto : `bool` | None
            Whether or not in auto range
        set_range : `float` | None
            The measurement range
        integration_time : `float` | None
            The integration time. This is not used in this and will be removed
            in future xml changes
        """
        if mode is None:
            mode = self.mode
        if auto is None:
            auto = self.auto_range
        if set_range is None:
            set_range = self.range
        if integration_time is None:
            integration_time = self.integration_time
        # TO-DO : Remove integration time from perform_zero_calibration

        await self.send_command(
            self.commands.perform_zero_calibration(mode, auto, set_range, integration_time)
        )
        await asyncio.sleep(ZERO_CALIBRATION_DELAY)
        await self.check_error("perform_zero_calibration")

        self.log.debug("Zero calibration command sent")
        await self.get_mode()
        await self.get_range()

    async def set_digital_filter(self, activate_filter, activate_avg_filter, activate_med_filter):
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
        self.filter_active = activate_filter
        filter_active = activate_avg_filter and activate_filter
        await self.send_command(f"{self.commands.activate_filter(self.mode, enums.Filter(2), filter_active)}")
        filter_active = activate_med_filter and activate_filter
        if self.electrometer_type == "Keithley" or self.mode == "CURR":
            await self.send_command(
                f"{self.commands.activate_filter(self.mode, enums.Filter(1), filter_active)}"
            )
        await self.get_avg_filter_status()
        if self.electrometer_type == "Keithley" or self.mode == "CURR":
            await self.get_med_filter_status()
        await self.check_error("set_digital_filter")

    async def get_avg_filter_status(self):
        """Get and cache the average filter status."""
        res = await self.send_command(f"{self.commands.get_filter_status(self.mode, 2)}", has_reply=True)
        self.log.debug(f"Average filter response is {res}")
        if res == "":
            self.avg_filter_active = False
        else:
            self.avg_filter_active = bool(int(res))

    async def get_med_filter_status(self):
        """Get and cache the median filter status."""
        if self.electrometer_type == "Keithley" or self.mode == "CURR":
            res = await self.send_command(f"{self.commands.get_filter_status(self.mode, 1)}", has_reply=True)
        else:
            self.log.debug(f"Keysight electrometer has mode {self.mode}. No median filter.")
            res = 0
        self.log.debug(f"median filter response is {res}")
        self.median_filter_active = bool(int(res))

    async def setup_scan(self):
        """Set up the electrometer to prepare for a scan."""
        await self.send_command(self.commands.set_resolution(mode=self.mode, digit=7))
        await self.send_command(self.commands.enable_sync(False))
        await self.send_command(f"{self.commands.output_trigger_line(3)}")
        await self.send_command(f"{self.commands.clear_buffer()}")

    async def prepare_scan(self):
        """Prepare the electrometer trace format for scanning."""
        await self.setup_scan()

        format_trac_args = {}
        if self.accessories.temperature:
            format_trac_args["temperature"] = True
        if self.accessories.vsource:
            format_trac_args["voltage"] = True
        format_trac_args["set_mode"] = True
        format_trac_args["mode"] = self.mode
        await self.send_command(self.commands.format_trac(**format_trac_args))

    async def start_scan(self, group_id=None):
        """Start storing values in the Keithley electrometer's buffer.

        Parameters
        ----------
        group_id : `str` | None
            Optional observing group identifier to store with the scan.
        """
        self.group_id = group_id
        await self.prepare_scan()
        await self.perform_zero_calibration()
        await self.send_command(f"{self.commands.clear_buffer()}")
        if self.electrometer_type == "Keysight":
            await self.send_command(f"{self.commands.clear_array()}")

        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.set_buffer_size(50000)}")

        await self.send_command(f"{self.commands.select_source(source=enums.Source.TIM)}")

        await self.send_command(f"{self.commands.set_infinite_triggers()}")

        await self.send_command(f"{self.commands.enable_display(False)}")
        if self.mode == "CHAR":
            await self.send_command(f"{self.commands.set_autodischarge('OFF')}")
            await self.send_command(f"{self.commands.discharge_capacitor()}")
        await self.send_command(f"{self.commands.start_storing_buffer()}")
        await self.send_command(f"{self.commands.acquire_data()}")
        self.manual_start_time = utils.current_tai()

    async def start_scan_dt(self, scan_duration, group_id=None):
        """Start storing values in the Keithley electrometer's buffer, for a
        set duration.

        Parameters
        ----------
        scan_duration : `float`
            The amount of time to store values for.
        group_id : `str` | None
            Optional observing group identifier to store with the scan.
        """
        self.group_id = group_id
        await self.prepare_scan()
        await self.perform_zero_calibration()
        await self.send_command(f"{self.commands.clear_buffer()}")
        if self.electrometer_type == "Keysight":
            await self.send_command(f"{self.commands.clear_array()}")

        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.set_buffer_size(50000)}")

        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.select_source(source=enums.Source.IMM)}")
        else:
            await self.send_command(f"{self.commands.select_source(source=enums.Source.TIM)}")
            await self.send_command(f"{self.commands.set_infinite_triggers()}")

        await self.send_command(f"{self.commands.enable_display(False)}")
        if self.mode == "CHAR":
            await self.send_command(f"{self.commands.set_autodischarge('OFF')}")
            await self.send_command(f"{self.commands.discharge_capacitor()}")
        await self.send_command(f"{self.commands.start_storing_buffer()}")
        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.next_read()}")
        self.manual_start_time = utils.current_tai()

        await self.continuous_scan(scan_duration)

    async def continuous_scan(self, scan_duration):
        """Collect readings for a timed Keithley scan.

        Parameters
        ----------
        scan_duration : `float`
            Length of time to collect readings, in seconds.
        """
        dt = 0
        while dt < scan_duration:
            await asyncio.sleep(self.integration_time)
            dt = utils.current_tai() - self.manual_start_time

    async def stop_scan(self) -> ScanResult:
        """Stop storing values and read the scan buffer.

        Returns
        -------
        scan_result : `ScanResult`
            Parsed scan data and scan metadata.
        """
        self.log.debug("Stopping scan")
        self.manual_end_time = utils.current_tai()
        self.scan_duration = self.manual_end_time - self.manual_start_time
        if self.electrometer_type == "Keysight":
            await self.send_command(f"{self.commands.stop_taking_data()}")
        await self.send_command(f"{self.commands.stop_storing_buffer()}")
        self.log.debug("Scanning stopped.")

        await self.send_command(f"{self.commands.enable_display(True)}")
        await asyncio.sleep(SLEEP)
        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.enable_zero_check(True)}")
        # FIXME: DM-37459
        # How long it takes to readout the buffer is dependent upon the
        # integration time and number of samples.
        # There is a bug in how the integration time is handled so
        # assume 0.2 seconds per sample for now until the bug
        # affecting the integration time is fixed.
        # Rough tests showed 330 data   points takes ~4s
        # Number of lines is approximately scan_duration over integration time
        # PF: based on test
        num_of_lines = self.scan_duration / ((self.integration_time * 3.07) + 0.00254)
        self.log.debug(f"approximate number of lines: {num_of_lines}")
        # Add extra time to read_timeout using num_of_lines times time per
        # sample time (assumption with 330 samples take ~4 seconds) with
        # approximately 30% overhead. Multiply by 2 for data and time
        read_timeout = self.commander.timeout + 3 + ((num_of_lines * TIME_PER_LINE) * OVERHEAD_FACTOR * 2)
        read_timeout = max(read_timeout, 10)
        self.read_timeout = read_timeout
        self.log.debug(f"{self.scan_duration=} so read timeout will be {read_timeout=}")
        self.log.debug("Starting to read buffer")
        res = await self.send_command(f"{self.commands.read_buffer()}", has_reply=True, timeout=read_timeout)
        # get the format of the data
        await asyncio.sleep(SLEEP)
        trace_format = await self.send_command(f"{self.commands.get_trace_format()}", has_reply=True)
        trace_elements = trace_format.split(",")
        trace_elements = [item for item in trace_elements if item not in ["STAT", "UNIT"]]
        self.log.debug(f"data format is {trace_elements}, number of categories is {len(trace_elements)}")
        data = self.parse_buffer(res, num_categories=len(trace_elements))

        return ScanResult(
            data=data,
            trace_elements=trace_elements,
            start_time=self.manual_start_time,
            end_time=self.manual_end_time,
            duration=self.scan_duration,
            group_id=self.group_id,
        )

    async def get_mode(self):
        """Get and cache the measurement mode."""
        res = await self.send_command(f"{self.commands.get_mode()}", has_reply=True)
        self.log.debug(f"Mode returns {res}")
        if str(res) in ['"CURR"', '"CHAR"', '"VOLT"', '"RES"']:
            mode = res
        elif str(res) == '"VOLT","CHAR"':
            _, mode = res.split(",")
        else:
            try:
                mode, unit = res.split(":")
            except Exception as e:
                msg = f"Mode does not have a recognizable format {e}"
                self.log.exception(msg)
                mode = '"CURR"'  # TO-DO remove once everything working

        mode = mode.replace('"', "")

        self.log.debug(f"Mode is {mode}")

        self.mode = enums.UnitMode(mode).name
        # TO-DO: Change XML so that evt_measureType write mode as a str
        # DM-45177

    async def get_intensity(self):
        """Get and cache the latest intensity reading."""
        res = await self.send_command(
            f"{self.commands.get_measure(enums.ReadingOption.LATEST)}", has_reply=True
        )
        res = res.split(",")
        # +9.90000+E37O with an O not zero
        try:
            if len(res) == 1:
                self.last_value = float(res[0])
            else:
                self.last_value = float(res[-1])
        except ValueError:
            self.last_value = float("inf")
            return  # return early
        # If the range saturates the intensity positively, the device returns
        # +9.90000+E37
        if float(res[-1]) == self.positive_saturation:
            self.log.debug("Positive saturation reached")
            self.last_value = float("inf")
        self.log.debug(f"last value is {self.last_value}")

    async def set_integration_time(self, int_time):
        """Set the integration time.

        Parameters
        ----------
        int_time : `float`
            The integration time.
        """
        self.integration_time = int_time

        await self.send_command(self.commands.auto_nplc_on(mode=self.mode))

        await self.send_command(self.commands.integration_time(self.mode, time=int_time))

        await self.get_integration_time()

    async def get_timer(self):
        """Get and cache the NPLC timer value."""
        self.nplc = float(await self.send_command(self.commands.get_timer(self.mode), has_reply=True))

    async def set_timer(self, nplc):
        """Set the NPLC timer value.

        Parameters
        ----------
        nplc : `float`
            Number of power line cycles.
        """
        await self.send_command(self.commands.auto_integration_time_on(mode=self.mode))
        await self.send_command(self.commands.set_timer(self.mode, nplc))
        await self.get_timer()
        await self.get_integration_time()

    async def set_mode(self, mode):
        """Set the mode/unit.

        Parameters
        ----------
        mode : `int`
            The mode of the electrometer.
        """
        # TO-DO: Change XML so that evt_measureType write mode as a str
        # DM-45177
        if mode in ["CURR", "CHAR", "VOLT", "RES"]:
            self.mode = mode
        else:
            self.mode = self.modes[mode].name

        await self.perform_zero_calibration()
        await self.check_error("set_mode")

        await self.get_mode()

    async def set_range(self, set_range):
        """Set the range.

        Parameters
        ----------
        set_range : `float`
            The new range value.
        """
        self.range = set_range
        if int(set_range) == -1:
            self.log.debug("Auto Range set")
            self.auto_range = True
        else:
            self.auto_range = False

        await self.perform_zero_calibration()
        await self.check_error("set_range")

        await self.get_range()

    def make_primary_header(self, scan_result: ScanResult, fits_data) -> fits.PrimaryHDU:
        """Make the primary FITS header.

        Parameters
        ----------
        scan_result : `ScanResult`
            Scan data and timing metadata.
        fits_data : object
            Object with ``index``, ``name``, and ``obs_ids`` attributes.

        Returns
        -------
        primary_hdu : `astropy.io.fits.PrimaryHDU`
            Primary HDU containing Rubin Observatory metadata.
        """
        primary_hdu = fits.PrimaryHDU()
        primary_hdu.header["FORMAT_V"] = ("1", "Header format version")
        primary_hdu.header["ORIGIN"] = "Vera C. Rubin Observatory"
        primary_hdu.header["INSTRUME"] = (
            f"Electrometer_index_{fits_data.index}",
            "Type of Instrument",
        )
        primary_hdu.header["MODEL"] = (self.model_id, "Model of instrument")
        primary_hdu.header["LOCATN"] = (self.location, "Location of Instrument")
        primary_hdu.header["CSCNAME"] = (
            fits_data.name,
            "Name of the CSC that produced this data.",
        )
        primary_hdu.header["DATE-BEG"] = (
            scan_result.start_time,
            "When start scan command sent to CSC (TAI)",
        )
        primary_hdu.header["DATE-END"] = (
            scan_result.end_time,
            "When stop scan command sent to CSC (TAI)",
        )
        primary_hdu.header["TIMESYS"] = ("TAI", "Format of timestamps")
        primary_hdu.header["SCANTIME"] = (scan_result.duration, "Duration of scan [s]")
        primary_hdu.header["SAMPTIME"] = (
            self.integration_time,
            "Duration of each sample [s]",
        )
        primary_hdu.header["FILTMED"] = (
            self.median_filter_active,
            "Median Filter Active",
        )
        primary_hdu.header["FILTAVG"] = (
            self.avg_filter_active,
            "Average Filter Active",
        )
        primary_hdu.header["IMGTYPE"] = (
            self.mode,
            "Options are charge, voltage, current",
        )
        primary_hdu.header["SENSBRND"] = (self.sensor_brand, "Sensor brand")
        primary_hdu.header["SENSMODL"] = (self.sensor_model, "Sensor model")
        primary_hdu.header["SERIAL"] = (self.sensor_serial, "Sensor serial number")
        primary_hdu.header["TEMP"] = (
            self.temperature,
            "Measurement from probe if attached and declared (Celsius)",
        )
        primary_hdu.header["VSOURCE"] = (
            self.vsource,
            "Voltage input if active and attached",
        )
        return primary_hdu

    async def write_fits_file(self, scan_result: ScanResult, data_format: list[str], fits_data) -> io.BytesIO:
        """Write scan data to an in-memory FITS file.

        Parameters
        ----------
        scan_result : `ScanResult`
            Scan data and timing metadata.
        data_format : `list` [`str`]
            Column names for the parsed scan data.
        fits_data : object
            Object with ``index``, ``name``, and ``obs_ids`` attributes.

        Returns
        -------
        file_upload : `io.BytesIO`
            FITS file content positioned at the beginning of the stream.
        """
        self.log.debug("Making primary header")
        primary_hdu = self.make_primary_header(scan_result=scan_result, fits_data=fits_data)
        self.log.debug("Primary header complete")
        data_metadata = {"name": "Single Electrometer scan readout"}
        data_format = [
            item.strip() for item in data_format if item not in ["STAT", "UNIT"]
        ]  # unique to Keithley and are not floats
        data_format = ["Elapsed Time" if (item == "TST" or item == "TIME") else item for item in data_format]

        data_format = [
            "Signal" if (item in ["CURR", "CHAR", "VOLT", "RES", "READ"]) else item for item in data_format
        ]

        if self.electrometer_type == "Keithley":
            _format = ["Signal", "RNUM", "Elapsed Time"]
            if len(data_format) == 3 and set(_format).issuperset(set(data_format)):
                data_format = _format
                self.log.debug(f"Changed data format for Keithley: {data_format}")

        data = {header: scan_result.data[i] for i, header in enumerate(data_format)}
        self.log.debug("Making data table")
        data_table = table.QTable(data=data, meta=data_metadata)
        table_hdu = fits.table_to_hdu(data_table)
        self.log.debug("Making fits file")
        hdul = fits.HDUList([primary_hdu, table_hdu])
        hdul[0].header["CALIBCLS"] = "lsst.ip.isr.PhotodiodeCalib"
        hdul[0].header["OBSID"] = fits_data.obs_ids[0]
        hdul[0].header["GROUPID"] = self.group_id

        file_upload = io.BytesIO()
        hdul.writeto(file_upload)
        file_upload.seek(0)
        return file_upload

    async def check_error(self, from_command: str | None):
        """Drain and log the electrometer error queue.

        Parameters
        ----------
        from_command : `str` | None
            Command name that triggered the error check.
        """

        async def get_error():
            """Read and parse one error from the electrometer queue."""
            res = await self.send_command(self.commands.get_last_error(), has_reply=True)
            try:
                error_code, message = res.split(",", maxsplit=1)
                return int(error_code), message
            except Exception as e:
                raise RuntimeError(f"Malformed error response from electrometer: {res!r}") from e

        async with asyncio.timeout(ERROR_DRAIN_TIMEOUT):
            for _ in range(MAX_ERROR_DRAIN):
                error_code, message = await get_error()
                if error_code == 0:
                    return
                self.log.warning(f"Non zero error code from {from_command}: {error_code=} {message=}")

        self.log.warning(
            f"Electrometer error queue did not drain after "
            f"{MAX_ERROR_DRAIN} reads from {from_command}: "
            f"{error_code=} {message=}"
        )

    async def get_range(self):
        """Get and cache the measurement range.

        Returns
        -------
        range : `float`
            Current measurement range.
        """
        res = await self.send_command(f"{self.commands.get_range(self.mode)}", has_reply=True)
        self.range = float(res)
        return self.range

    async def get_integration_time(self):
        """Get and cache the integration time.

        Returns
        -------
        integration_time : `float`
            Current integration time, in seconds.
        """
        res = await self.send_command(f"{self.commands.get_integration_time(self.mode)}", has_reply=True)
        self.integration_time = float(res)
        return self.integration_time

    async def toggle_voltage_source(self, toggle):
        """Enable or disable the voltage source.

        Parameters
        ----------
        toggle : `bool`
            Whether to enable the voltage source.
        """
        await self.send_command(self.commands.toggle_voltage_source(toggle))
        await self.get_voltage_source_status()

    async def get_voltage_source_status(self):
        """Get and cache the voltage source status.

        Returns
        -------
        voltage_source : `bool`
            Whether the voltage source is enabled.
        """
        res = await self.send_command(self.commands.get_voltage_source_status(), has_reply=True)
        match str(res).strip().upper():
            case "ON":
                self.voltage_source = True
            case "OFF":
                self.voltage_source = False
            case _:
                self.voltage_source = bool(int(res))
        return self.voltage_source

    async def get_voltage_range(self):
        """Get and cache the voltage source range.

        Returns
        -------
        voltage_range : `int`
            Voltage source range.
        """
        res = await self.send_command(self.commands.get_voltage_range(), has_reply=True)
        self.voltage_range = int(res)
        return self.voltage_range

    async def set_voltage_range(self, range):
        """Set the voltage source range.

        Parameters
        ----------
        range : `int`
            Voltage source range.
        """
        await self.send_command(self.commands.set_voltage_range(range))
        await self.get_voltage_range()

    async def get_voltage_limit(self):
        """Get and cache the voltage source limit.

        Returns
        -------
        voltage_limit : `int`
            Voltage source limit.
        """
        res = await self.send_command(self.commands.get_voltage_limit(), has_reply=True)
        self.voltage_limit = int(res)
        return self.voltage_limit

    async def set_voltage_limit(self, limit):
        """Set the voltage source limit.

        Parameters
        ----------
        limit : `int`
            Voltage source limit.
        """
        await self.send_command(self.commands.set_voltage_limit(limit))
        await self.get_voltage_limit()

    async def get_voltage_level(self):
        """Get and cache the voltage source level.

        Returns
        -------
        voltage_level : `int`
            Voltage source level.
        """
        res = await self.send_command(self.commands.get_voltage_level(), has_reply=True)
        self.voltage_level = int(res)
        return self.voltage_level

    async def set_voltage_level(self, level):
        """Set the voltage source level.

        Parameters
        ----------
        level : `int`
            Voltage source level.
        """
        await self.send_command(self.commands.set_voltage_level(amplititude=level))
        await self.get_voltage_level()


class KeithleyElectrometerController(ElectrometerController):
    """Provide high-level control for a Keithley electrometer.

    Parameters
    ----------
    log : `logging.Logger` or `None`, optional
        Logger for controller messages. If `None`, a logger named for this
        class is created.
    """

    def __init__(self, log=None):
        super().__init__(log=log)
        self.commands = commands_factory.KeithleyElectrometerCommandFactory()
        # Intensity value when saturated in the positive direction.
        self.positive_saturation = 9.9e37

    @classmethod
    def get_config_schema(cls):
        """Return the JSON schema for Keithley-specific configuration."""
        return yaml.safe_load(
            """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_electrometer/blob/main/schema/Keithley.yaml
title: Keithley v7
description: Schema for Keithley Electrometer configuration files.
type: object
properties: {}
additionalProperties: false
"""
        )

    def configure(self, config):
        """Configure the Keithley controller.

        Parameters
        ----------
        config : `types.SimpleNamespace`
            Configuration for one electrometer instance.
        """
        super().configure(config)


class KeysightElectrometerController(ElectrometerController):
    """Provide high-level control for a Keysight electrometer.

    Parameters
    ----------
    log : `logging.Logger` or `None`, optional
        Logger for controller messages. If `None`, a logger named for this
        class is created.
    """

    def __init__(self, log=None):
        super().__init__(log=log)
        self.commands = commands_factory.KeysightElectrometerCommandFactory()
        # Intensity value when saturated in the positive direction.
        self.positive_saturation = 9.91e37

    @classmethod
    def get_config_schema(cls):
        """Return the JSON schema for Keysight-specific configuration."""
        return yaml.safe_load(
            """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_electrometer/blob/main/schema/Keysight.yaml
title: Keysight v7
description: Schema for Keysight Electrometer configuration files.
type: object
properties: {}
"""
        )

    async def setup_scan(self):
        """Set up the Keysight electrometer to prepare for a scan."""
        await self.send_command(f"{self.commands.output_trigger_line()}")
        await self.send_command(f"{self.commands.clear_buffer()}")

    async def continuous_scan(self, scan_duration):
        """Acquire data for a timed Keysight scan.

        Parameters
        ----------
        scan_duration : `float`
            Length of time to acquire data, in seconds.
        """
        await self.send_command(f"{self.commands.acquire_data()}")
        await asyncio.sleep(scan_duration)
        await self.send_command(f"{self.commands.stop_taking_data()}")

    def configure(self, config):
        """Configure the Keysight controller.

        Parameters
        ----------
        config : `types.SimpleNamespace`
            Configuration for one electrometer instance.
        """
        super().configure(config)
