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
import io
import logging
import pathlib
import re
import types

import astropy.io.fits as fits
import astropy.time
import numpy as np
import yaml
from astropy import table
from lsst.ts import utils

from . import commander, commands_factory, enums

TIME_PER_LINE = 0.0047
"""The time per line is calculated based on the result that 200 samples takes
~4 seconds."""
OVERHEAD_FACTOR = 1.3
"""Assume a 30% overhead when gathering data from the buffer."""


class ElectrometerController(abc.ABC):
    """Class that provides high level control for electrometer.

    Parameters
    ----------
    csc : `ElectrometerCSC`
        A copy of the CSC.
    log : `None` or `logging.Logger`
        A logger.

    Attributes
    ----------
    commander : `commander.Commander`
        The tcpip interface for writing and reading from the device.
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
    modes : `dict`
        Associate SAL Command number with electrometer UnitMode enum.
    voltage_status : `bool`
        Is voltage source enabled.
    temperature : `float`
        The temperature (deg_C) returned from the probe.
    vsource : `float`
        The voltage (V) source input.
    """

    def __init__(self, csc, log=None):
        # Create a logger if none were passed during the instantiation of
        # the class
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)

        self.csc = csc
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
        self.log.debug("Controller initialized")
        self.group_id = None

    @property
    def connected(self):
        return self.commander.connected

    def parse_buffer(self, response, num_categories=2):
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
        voltage : `list`
            The voltage values.
        """
        regex_numbers = r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"
        # regex_strings = "(?!E+)[a-zA-Z]+"
        self.log.debug(f"response: {response}")
        raw_values = list(map(float, re.findall(regex_numbers, response)))
        self.log.debug(f"parse_buffer: {raw_values=}")

        # Converting each value to a float
        raw_str_values = [float(value) for value in raw_values]

        # Creating separate lists for each category
        categorized_lists = [[] for _ in range(num_categories)]
        for i, value in enumerate(raw_str_values):
            category_index = i % num_categories
            categorized_lists[category_index].append(value)
        self.log.debug(f"number of categories: {num_categories}")
        self.log.debug(f"categorized lists: {categorized_lists}")
        return categorized_lists

    @abc.abstractmethod
    def configure(self, config):
        self.default = types.SimpleNamespace(
            mode=config.mode,
            range=config.range,
            filters=types.SimpleNamespace(**config.filters),
            integration_time=config.integration_time,
        )
        self.mode = enums.UnitMode(self.modes[config.mode])
        self.range = config.range
        tcpip = types.SimpleNamespace(**config.tcpip)
        self.commander = commander.Commander(
            log=self.log, brand=config.electrometer_type
        )
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

    @classmethod
    @abc.abstractmethod
    def get_config_schema(cls):
        pass

    async def send_command(self, command, has_reply=False, timeout=None):
        return await self.commander.send_command(
            msg=command,
            has_reply=has_reply,
            timeout=timeout,
        )

    async def connect(self):
        self.image_service_client = utils.ImageNameServiceClient(
            url=self.image_name_service,
            csc_index=self.csc.salinfo.index,
            source="Electrometer",
        )
        await self.commander.connect()
        id = await self.send_command(
            command=self.commands.get_hardware_info(), has_reply=True
        )
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
        match expected_type:
            case "Keithley":
                await self.send_command(command=self.commands.output_trigger_line(3))
            case "Keysight":
                await self.send_command(command=self.commands.output_trigger_line())
        self.log.debug("Device reset.")
        await self.perform_zero_calibration(
            mode=enums.UnitMode(self.modes[self.default.mode]),
            auto=self.auto_range,
            set_range=self.default.range,
            integration_time=self.default.integration_time,
        )
        await self.set_digital_filter(
            activate_filter=self.default.filters.general,
            activate_avg_filter=self.default.filters.average,
            activate_med_filter=self.default.filters.median,
        )

    async def disconnect(self):
        self.image_service_client = None
        await self.commander.disconnect()

    async def perform_zero_calibration(self, mode, auto, set_range, integration_time):
        if mode is None:
            mode = self.mode
        if auto is None:
            auto = self.auto_range
        if set_range is None:
            set_range = self.range
        if integration_time is None:
            integration_time = self.integration_time

        self.log.debug(f"Mode being sent to Set Range: {enums.UnitMode(mode).name}")
        self.log.debug(
            f"perform zero calibs params: {mode, auto, set_range, integration_time}"
        )
        await self.send_command(
            self.commands.perform_zero_calibration(
                mode, auto, set_range, integration_time
            )
        )
        self.log.debug("Zero calibration command sent")
        await asyncio.sleep(3)
        await self.get_mode()
        await self.get_range()
        await self.get_integration_time()
        await self.check_error("perform_zero_calibration")
        self.log.debug("Zero Calibration sent to controller")

    async def set_digital_filter(
        self, activate_filter, activate_avg_filter, activate_med_filter
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
        self.log.debug(f"filter_type is {enums.Filter(2)}")
        filter_active = activate_avg_filter and activate_filter
        await self.send_command(
            f"{self.commands.activate_filter(self.mode, enums.Filter(2), filter_active)}"
        )
        filter_active = activate_med_filter and activate_filter
        self.log.debug(f"filter_type is {enums.Filter(1)}")
        await self.send_command(
            f"{self.commands.activate_filter(self.mode, enums.Filter(1), filter_active)}"
        )
        await self.csc.evt_digitalFilterChange.set_write(activateFilter=filter_active)
        await self.get_avg_filter_status()
        await self.get_med_filter_status()
        await self.check_error("set_digital_filter")

    async def get_avg_filter_status(self):
        """Get the average filter status."""
        res = await self.send_command(
            f"{self.commands.get_filter_status(self.mode, 2)}", has_reply=True
        )
        self.log.debug(f"Average filter response is {res}")
        if res == "":
            self.avg_filter_active = False
        else:
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

    async def prepare_scan(self):
        """Prepare the keithley for scanning."""
        if self.electrometer_type == "Keithley":
            await self.send_command(
                self.commands.set_resolution(mode=self.mode, digit=7)
            )
        await self.send_command(self.commands.enable_sync(False))

        await self.perform_zero_calibration(
            self.mode, self.auto_range, self.range, self.integration_time
        )
        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.output_trigger_line(3)}")
        elif self.electrometer_type == "Keysight":
            await self.send_command(f"{self.commands.output_trigger_line()}")
        await self.send_command(f"{self.commands.clear_buffer()}")
        format_trac_args = {}
        if self.accessories.temperature:
            format_trac_args["temperature"] = True
        if self.accessories.vsource:
            format_trac_args["voltage"] = True
        format_trac_args["set_mode"] = True
        format_trac_args["mode"] = self.mode.name
        await self.send_command(self.commands.format_trac(**format_trac_args))

    async def start_scan(self, group_id=None):
        """Start storing values in the Keithley electrometer's buffer."""
        self.group_id = group_id
        await self.prepare_scan()
        await self.send_command(f"{self.commands.clear_buffer()}")
        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.set_buffer_size(50000)}")
        await self.send_command(
            f"{self.commands.select_source(source=enums.Source.TIM)}"
        )
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
        """
        self.group_id = group_id
        await self.prepare_scan()
        await self.send_command(f"{self.commands.clear_buffer()}")
        if self.electrometer_type == "Keithley":
            await self.send_command(f"{self.commands.set_buffer_size(50000)}")
        await self.send_command(
            f"{self.commands.select_source(source=enums.Source.IMM)}"
        )
        await self.send_command(f"{self.commands.enable_display(False)}")
        if self.mode == "CHAR":
            await self.send_command(f"{self.commands.set_autodischarge('OFF')}")
            await self.send_command(f"{self.commands.discharge_capacitor()}")
        await self.send_command(f"{self.commands.start_storing_buffer()}")
        await self.send_command(f"{self.commands.next_read()}")
        self.manual_start_time = utils.current_tai()

        if self.electrometer_type == "Keysight":
            await asyncio.sleep(scan_duration)
            await self.send_command(f"{self.commands.stop_taking_data()}")
        elif self.electrometer_type == "Keithley":
            dt = 0
            while dt < scan_duration:
                await self.get_intensity()
                await self.csc.evt_intensity.set_write(intensity=self.last_value)
                await asyncio.sleep(self.integration_time)
                dt = utils.current_tai() - self.manual_start_time

    async def stop_scan(self):
        """Stop storing values in the electrometer."""
        self.log.debug("Stopping scan")
        self.manual_end_time = utils.current_tai()
        self.scan_duration = self.manual_end_time - self.manual_start_time
        if self.electrometer_type == "Keysight":
            await self.send_command(f"{self.commands.stop_taking_data()}")
        await self.send_command(f"{self.commands.stop_storing_buffer()}")
        self.log.debug("Scanning stopped.")
        await self.get_intensity()
        self.log.debug("get_intensity complete")
        self.log.debug(f"last value is {self.last_value}")
        await self.csc.evt_intensity.set_write(intensity=self.last_value)
        await self.send_command(f"{self.commands.enable_display(True)}")
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
        read_timeout = (
            self.commander.timeout
            + 3
            + ((num_of_lines * TIME_PER_LINE) * OVERHEAD_FACTOR * 2)
        )
        read_timeout = max(read_timeout, 10)
        self.log.debug(f"{self.scan_duration=} so read timeout will be {read_timeout=}")
        self.log.debug("Starting to read buffer")
        res = await self.send_command(
            f"{self.commands.read_buffer()}", has_reply=True, timeout=read_timeout
        )
        # get the format of the data
        trace_format = await self.send_command(
            f"{self.commands.get_trace_format()}", has_reply=True
        )
        trace_elements = trace_format.split(",")
        trace_elements = [
            item for item in trace_elements if item not in ["STAT", "UNIT"]
        ]
        self.log.debug(
            f"data format is {trace_elements}, number of categories is {len(trace_elements)}"
        )
        data = self.parse_buffer(res, num_categories=len(trace_elements))

        await self.write_fits_file(data, trace_elements)

    async def get_mode(self):
        """Get the mode/unit."""
        res = await self.send_command(f"{self.commands.get_mode()}", has_reply=True)
        self.log.debug(f"Mode returns {res}")
        if res not in ["CHAR", "RES", "VOLT", "CURR"]:
            self.log.debug(f"HERE ({res})")
            mode, unit = res.split(":")
            mode = mode.replace('"', "")
        else:
            mode = res
            mode = mode.replace('"', "")

        self.log.debug(f"Mode is {mode}")

        self.mode = enums.UnitMode(mode)
        await self.csc.evt_measureType.set_write(
            mode=int([num for num, mode in self.modes.items() if self.mode == mode][0]),
            force_output=True,
        )
        # TO-DO: Change XML so that evt_measureType write mode as a str
        # DM-45177

    async def get_intensity(self):
        """Get the intensity."""
        res = await self.send_command(
            f"{self.commands.get_measure(enums.ReadingOption.LATEST)}", has_reply=True
        )
        self.log.debug(f"intensity is {res}")
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
        self.log.debug(f"Positive saturation is {self.positive_saturation}")
        if res == self.positive_saturation:
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
        self.log.debug(f"{int_time=}")
        await self.send_command(
            f"{self.commands.integration_time(mode=self.mode, time=self.integration_time)}"
        )
        await self.get_integration_time()
        await self.check_error("set_integration_time")

    async def set_mode(self, mode):
        """Set the mode/unit.

        Parameters
        ----------
        mode : `int`
            The mode of the electrometer.
        """
        self.mode = enums.UnitMode(self.modes[mode])
        self.log.debug(f"Set mode {self.mode}")

        await self.perform_zero_calibration(
            self.mode, self.auto_range, self.range, self.integration_time
        )

    async def set_range(self, set_range):
        """Set the range.

        Parameters
        ----------
        set_range : `float`
            The new range value.
        """
        self.range = set_range
        self.log.debug(f"{set_range=}")
        if int(set_range) == -1:
            self.log.debug("Auto Range set")
            self.auto_range = True
        else:
            self.auto_range = False

        await self.perform_zero_calibration(
            self.mode, self.auto_range, self.range, self.integration_time
        )

    def make_primary_header(self):
        """Make primary header for fits file that follows Rubin Obs. format."""
        primary_hdu = fits.PrimaryHDU()
        primary_hdu.header["FORMAT_V"] = ("1", "Header format version")
        primary_hdu.header["ORIGIN"] = "Vera C. Rubin Observatory"
        primary_hdu.header["INSTRUME"] = (
            f"Electrometer_index_{self.csc.salinfo.index}",
            "Type of Instrument",
        )
        primary_hdu.header["MODEL"] = (self.model_id, "Model of instrument")
        primary_hdu.header["LOCATN"] = (self.location, "Location of Instrument")
        primary_hdu.header["CSCNAME"] = (
            self.csc.salinfo.name,
            "Name of the CSC that produced this data.",
        )
        primary_hdu.header["DATE-BEG"] = (
            self.manual_start_time,
            "When start scan command sent to CSC (TAI)",
        )
        primary_hdu.header["DATE-END"] = (
            self.manual_end_time,
            "When stop scan command sent to CSC (TAI)",
        )
        primary_hdu.header["TIMESYS"] = ("TAI", "Format of timestamps")
        primary_hdu.header["SCANTIME"] = (self.scan_duration, "Duration of scan [s]")
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
            "Measurement from probe if attached and declared (Celcius)",
        )
        primary_hdu.header["VSOURCE"] = (
            self.vsource,
            "Voltage input if active and attached",
        )
        return primary_hdu

    async def write_fits_file(self, raw_data, data_format):
        """Write fits file of the intensity, time, and temperature values.

        Parameters
        ----------
        signal : `list` of `float`
            The amount of photons in a given reading, unit depends on mode of
            electrometer.
            * Curr: Ampere - Measure current
            * Volt: V - Measure volts
            * Char: Coulomb - Measure charge
        times : `list` of `float`
            The time (TAI) of the signal data taken.
        temperature : `list` of `float`
            A consistent temperature value (deg_C) obtained from the
            temperature probe over the period of signal acquisition.
        unit : `list` of `str`
            The unit of the signal data. (constant)
        voltage : `list` of `float`
            The source input in Volts maintained during signal acquisition.
        """
        self.log.debug("Making primary header")
        primary_hdu = self.make_primary_header()
        self.log.debug("Primary header complete")
        data_metadata = {"name": "Single Electrometer scan readout"}
        self.log.debug(raw_data)
        self.log.debug(data_format)
        data_format = [
            item.strip() for item in data_format if item not in ["STAT", "UNIT"]
        ]  # unique to Keithley and are not floats
        data_format = [
            "Elapsed Time" if (item == "TST" or item == "TIME") else item
            for item in data_format
        ]

        data_format = [
            "Signal" if (item in ["CURR", "CHAR", "VOLT", "RES", "READ"]) else item
            for item in data_format
        ]

        data = {header: raw_data[i] for i, header in enumerate(data_format)}
        self.log.debug(f"Data is {data}")
        self.log.debug("Making data table")
        data_table = table.QTable(data=data, meta=data_metadata)
        table_hdu = fits.table_to_hdu(data_table)
        self.log.debug(f"Data table {data_table}")
        self.log.debug("Making fits file")
        hdul = fits.HDUList([primary_hdu, table_hdu])
        image_sequence_array, obs_ids = await self.image_service_client.get_next_obs_id(
            num_images=1
        )
        hdul[0].header["OBSID"] = obs_ids[0]
        hdul[0].header["GROUPID"] = self.group_id
        self.group_id = None
        filename = f"{obs_ids[0]}.fits"
        try:
            pathlib.Path(self.fits_file_path).mkdir(parents=True, exist_ok=True)
            hdul.writeto(f"{self.fits_file_path}/{filename}")
            signal = data["Signal"]
            self.log.info(
                f"Electrometer Scan data file written: {filename}\n"
                f"Scan Summary of Signal [Mean, median, std] is: "
                f"[{np.mean(signal):0.5e}, {np.median(signal):0.5e}, {np.std(signal):0.5e}]\n"
                f"Scan Summary of Time [Mean, median] is: "
                f"[{np.mean(data['Elapsed Time']):0.5e}, {np.median(data['Elapsed Time']):0.5e}]"
            )
        except Exception as e:
            msg = "Writing file to local disk failed."
            self.log.exception(msg)
            raise RuntimeError(e)
        try:
            file_upload = io.BytesIO()
            hdul.writeto(file_upload)
            file_upload.seek(0)
            key_name = self.csc.bucket.make_key(
                salname="Electrometer",
                salindexname=self.csc.salinfo.index,
                generator="fits",
                date=astropy.time.Time(self.manual_end_time, format="unix_tai"),
                suffix=".fits",
            )
            await self.csc.bucket.upload(fileobj=file_upload, key=key_name)
            url = (
                f"{self.csc.bucket.service_resource.meta.client.meta.endpoint_url}/"
                f"{self.csc.bucket.name}/{key_name}"
            )
            await self.csc.evt_largeFileObjectAvailable.set_write(
                url=url, generator=f"{self.csc.salinfo.name}:{self.csc.salinfo.index}"
            )
        except Exception:
            self.log.exception("Uploading file to s3 bucket failed.")

    async def check_error(self, from_command: str = None):
        """Check the error.
        Parameter
        ---------
            from_command : `str`
                Tells us where the check error is being called from
        """
        res = await self.send_command(
            f"{self.commands.get_last_error()}", has_reply=True
        )
        self.log.debug(f"check error from {from_command}: {res}")
        self.error_code, self.message = res.split(",")
        if self.message != "No Error":
            raise RuntimeError(f"Check Error: {res}")

    async def get_range(self):
        """Get the range value."""
        res = await self.send_command(
            f"{self.commands.get_range(self.mode)}", has_reply=True
        )
        self.log.debug(f"Get Range Output: {res}")
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

    async def toggle_voltage_source(self, toggle):
        await self.send_command(self.commands.toggle_voltage_source(toggle))
        await self.get_voltage_source_status()

    async def get_voltage_source_status(self):
        res = await self.send_command(
            self.commands.get_voltage_source_status(), has_reply=True
        )
        self.voltage_source = bool(res)
        await self.csc.evt_voltageSourceChanged.set_write(status=self.voltage_source)

    async def get_voltage_range(self):
        res = await self.send_command(self.commands.get_voltage_range(), has_reply=True)
        self.voltage_range = int(res)
        await self.csc.evt_voltageSourceChanged.set_write(range=self.voltage_range)

    async def set_voltage_range(self, range):
        await self.send_command(self.commands.set_voltage_range(range))
        await self.get_voltage_range()

    async def get_voltage_limit(self):
        res = await self.send_command(self.commands.get_voltage_limit(), has_reply=True)
        self.voltage_limit = int(res)
        await self.csc.evt_voltageSourceChanged.set_write(
            voltage_limit=self.voltage_limit
        )

    async def set_voltage_limit(self, limit):
        await self.send_command(self.commands.set_voltage_limit(limit))
        await self.get_voltage_limit()

    async def get_voltage_level(self):
        res = await self.send_command(self.commands.get_voltage_level(), has_reply=True)
        self.voltage_level = int(res)

    async def set_voltage_level(self, level):
        await self.send_command(self.commands.set_voltage_level(amplititude=level))
        await self.get_voltage_level()
        await self.csc.evt_voltageSourceChanged.set_write(level=self.voltage_level)


class KeithleyElectrometerController(ElectrometerController):
    """Class that provides high level control for the Keithley electrometer.
    It inherits methods from the general electrometer controller

    """

    def __init__(self, csc, log=None):
        super().__init__(csc, log=log)
        self.commands = commands_factory.KeithleyElectrometerCommandFactory()
        # Intensity value when saturated in the positive direction.
        self.positive_saturation = 9.9e37

    @classmethod
    def get_config_schema(cls):
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
        super().configure(config)


class KeysightElectrometerController(ElectrometerController):
    """Class that provides high level control for the Keithley electrometer.
    It inherits methods from the general electrometer controller

    """

    def __init__(self, csc, log=None):
        super().__init__(csc, log=log)
        self.commands = commands_factory.KeysightElectrometerCommandFactory()
        # Intensity value when saturated in the positive direction.
        self.positive_saturation = 9.91e37

    @classmethod
    def get_config_schema(cls):
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

    def configure(self, config):
        super().configure(config)
