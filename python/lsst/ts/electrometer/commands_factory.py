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

from . import enums


class ElectrometerCommandFactory:
    """Class that formats commands to control the electrometer via RS-232."""

    def __init__(self) -> None:
        pass

    def activate_filter(self, mode, filter_type, active) -> str:
        """Return activate filter command.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the filter to activate.
        filter_type : `Filter`
            The filter type to activate
        active : `int`
            Whether to activate or not.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).name}:{enums.Filter(filter_type).name}:stat {int(active)};"
        return command

    def get_avg_filter_status(self, mode) -> str:
        """Return average filter status.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the filter to check.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).name}:aver:type?;"
        return command

    def get_med_filter_status(self, mode) -> str:
        """Return median filter status.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the filter to check.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).name}:med:stat?;"
        return command

    def get_filter_status(self, mode, filter_type) -> str:
        """Return filter status.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the filter to check
        filter_type : `Filter`
            The type of the filter to check.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = (
            f":sens:{enums.UnitMode(mode).name}:{enums.Filter(filter_type).name}:stat?;"
        )
        return command

    def set_avg_filter_status(self, mode, aver_filter_type) -> str:
        """Return set average filter status.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the filter to set.
        aver_filter_type : `AverFilterType`
            The type of the average filter to set.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = (
            f":sens:{enums.UnitMode(mode).name}:aver:type "
            f"{enums.AverFilterType(aver_filter_type).name};"
        )
        return command

    def set_med_filter_status(self, mode, active) -> str:
        """Return set median filter status

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the filter to set.
        active : `int`
            Whether to activate.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).name}:med:stat {int(active)};"
        return command

    def always_read(self) -> str:
        """Return always read buffer.

        Returns
        -------
        commmand : `str`
            The generated command string.
        """
        command = f":trac:feed:cont alw;{self.init_buffer()}"
        return command

    def next_read(self):
        """Return next read buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":trac:feed:cont next;{self.init_buffer()}"
        return command

    def clear_buffer(self):
        """Return clear buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:cle;"
        return command

    def clear_device(self):
        """Return clear device.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "^C"
        return command

    def get_last_error(self):
        """Return get last error.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":syst:err?;"
        return command

    def format_trac(self, channel=False, timestamp=True, temperature=False):
        """Return format data stored to the buffer.

        Parameters
        ----------
        channel : `bool`
            Whether to store channel data.
        timestamp : `bool`
            Whether to store timestamp data.
        temperature : `bool`
            Whether to store temperature data.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        isFirst = True
        if not (timestamp or temperature or channel):
            command = ":trac:elem NONE"
        else:
            command = ":trac:elem "
            if channel:
                isFirst = False
                command += "CHAN"
            if timestamp:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "TST"
            if temperature:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "ETEM"
        command += ";"
        return command

    def get_buffer_quantity(self):
        """Return get buffer quantity.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:poin:act?;"
        return command

    def get_hardware_info(self):
        """Return get hardware info.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "*idn?"
        return command

    def get_measure(self, read_option):
        """Return get measure.

        Parameters
        ----------
        read_option : `ReadingOption`
            The reading option.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        if enums.ReadingOption(read_option) == enums.ReadingOption.LATEST:
            command = ":sens:data?;"
        else:
            command = ":sens:data:fres?;"
        return command

    def get_mode(self):
        """Return get mode.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":sens:func?;"
        return command

    def enable_temperature_reading(self, enable):
        """Return enable temperature reading.

        Parameters
        ----------
        enable : `bool`
            Whether to enable temperature reading.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        if enable:
            command = ":syst:tsc ON;"
        else:
            command = ":syst:tsc OFF;"
        return command

    def read_buffer(self):
        """Return read buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:data?;"
        return command

    def reset_device(self):
        """Return reset device.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f"*RST; {self.clear_buffer()}"
        return command

    def select_source(self, source=enums.Source.TIM):
        command = f":trig:sour {enums.Source(source)};"
        return command

    def select_device_timer(self, timer=0.001):
        """Return select device timer.

        Parameters
        ----------
        timer : `float`
            The internal device loop timer. Values below 0.001 can cause
            instability.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":trig:tim {timer:.3f};"
        return command

    def set_buffer_size(self, buffer_size=50000):
        """Return set buffer size.

        Parameters
        ----------
        buffer_size: `int`
            The number of values to store in the buffer.
            Maximum is 50000.
        """
        command = f"{self.clear_buffer()}:trac:points {str(buffer_size)};:trig:count {str(buffer_size)};"
        return command

    def init_buffer(self):
        """Return start storing readings into the buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":init;"
        return command

    def integration_time(self, mode, time=0.001):
        """Return integration time.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the aperature to set.
        time : `float`
            The integration time of the aperture.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).name}:aper {time:f};"
        return command

    def set_mode(self, mode):
        """Return set mode.

        Parameters
        ----------
        mode : `UnitMode`
            The unit to switch to.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:func '{enums.UnitMode(mode)}';"
        return command

    def set_range(self, auto, range_value, mode):
        """Return set range.

        Parameters
        ----------
        auto : `bool`
            Whether auto range is activated.
        range_value : `float`
            The range to set.
            Not used if auto is true.
        mode : `enums.UnitMode`
            The unit of the range to set.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        if auto:
            command = ":sens:" + enums.UnitMode(mode).name + ":rang:auto 1;"
        else:
            command = ":sens:" + enums.UnitMode(mode).name + ":rang:auto 0;"
            command += (
                "\n:sens:"
                + enums.UnitMode(mode).name
                + ":rang "
                + str(range_value)
                + ";"
            )
        return command

    def enable_sync(self, enable):
        """Return enable sync.

        Parameters
        ----------
        enable : `bool`
            Whether to enable sync.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":syst:lsyn:stat ON;" if enable else ":syst:lsyn:stat OFF;"
        return command

    def stop_storing_buffer(self):
        """Return stop storing buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:feed:cont NEV;"
        return command

    def enable_all_instrument_errors(self):
        """Return enable all instrument errors.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":stat:que:enab (-440:+958);"
        return command

    def enable_zero_check(self, enable):
        """Return enable zero check.

        Parameters
        ----------
        enable : `bool`
            Whether to enable zero check.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":syst:zch ON;" if enable else ":syst:zch OFF;"
        return command

    def enable_zero_correction(self, enable):
        """Return enable zero correction.

        Parameters
        ----------
        enable : `bool`
            Whether to enable zero correction.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":syst:zcor ON;" if enable else ":syst:zcor OFF;"
        return command

    def get_range(self, mode):
        """Return get range command string.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the range to check.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":sens:" + enums.UnitMode(mode).name + ":rang?;"
        return command

    def get_integration_time(self, mode):
        """Return get integration time command string.

        Parameters
        ----------
        mode : UnitMode
            The unit of the integration time to check.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":sens:" + enums.UnitMode(mode).name + ":aper?;"
        return command

    def enable_display(self, enable):
        """Return enable display command string.

        Parameters
        ----------
        enable : bool
            Whether to enable the display.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":disp:enab ON;" if enable is True else ":disp:enab OFF;"
        return command

    def set_timer(self, mode):
        """Return set time command string.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).lower()}:nplc 0.01;"
        return command

    def prepare_buffer(self):
        """Return combo of commands for prepare buffer command.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = (
            f"{self.clear_buffer()} "
            f" {self.format_trac(channel=False, timestamp=True, temperature=False)} "
            f"{self.set_buffer_size(50000)}"
        )
        return command

    def perform_zero_calibration(self, mode, auto, range_value):
        """Return combo of commands for perform zero calibration command.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the device
        auto : `bool`
            Whether auto range is activated.
        range_value : `float`
            The range of the values.

        Returns
        -------
        command : `str`
            The generated command string
        """
        command = (
            f"{self.enable_zero_check(True)} "
            f"{self.set_mode(mode)} "
            f" {self.set_range(auto=auto, range_value=range_value, mode=mode)} "
            f" {self.enable_zero_correction(enable=True)} "
            f"{self.enable_zero_check(False)}"
        )
        return command

    def disable_all(self):
        """Return combo of commands for disable all command.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f"{self.enable_sync(False)} :trig:del 0.0;"
        return command
