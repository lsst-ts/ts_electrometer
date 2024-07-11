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
    "ElectrometerCommandFactory",
    "KeithleyElectrometerCommandFactory",
    "KeysightElectrometerCommandFactory",
]

from . import enums


class ElectrometerCommandFactory:
    def __init__(self):
        pass

    def activate_filter(self, mode, filter_type, active):
        unit = enums.UnitMode(mode).name
        filter = enums.Filter(filter_type).name
        return f":sens:{unit}:{filter}:stat {int(active)};"

    def get_filter_status(self, mode, filter_type):
        unit = enums.UnitMode(mode).name
        filter = enums.Filter(filter_type).name
        return f":sens:{unit}:{filter}:stat?;"

    def always_read(self) -> str:
        """Return always read buffer.

        Returns
        -------
        commmand : `str`
            The generated command string. An array of all data in the buffer.
        """
        return f":trac:feed:cont alw;{self.init_buffer()}"

    def next_read(self):
        """Return the latest measurement data from buffer

        Returns
        -------
        command : `str`
            The generated command string.
        """
        return f":trac:feed:cont NEXT;{self.init_buffer()}"

    def acquire_data(self):
        """Returns the command to start acquiring data

        Returns
        -------
        command : `str`
            The generated command string
        """
        return f":trac:feed:cont NEXT;{self.init_buffer()}"

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

    def format_trac(
        self,
        timestamp=True,
        temperature=False,
        voltage=False,
        set_mode=False,
        mode="VOLT",
        channel=False,
    ):
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
        self.data_columns = 1
        if not (timestamp or temperature or voltage or set_mode):
            command = ":trac:elem NONE"
        else:
            command = ":trac:elem "
            if channel:
                isFirst = False
                command += "CHAN"
                self.data_columns += 1
            if timestamp:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "TST"
                self.data_columns += 1
            if temperature:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "ETEM"
                self.data_columns += 1
            if voltage:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "VSO"
                self.data_columns += 1
            if set_mode:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += f"{mode}"
                self.data_columns += 1
        command += ";"
        return command

    def get_trace_format(self):
        """Returns the format of the trace.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:elem?"
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

    def set_autodischarge(self, autodischarge_state):
        """Sets the autodischarge state.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f"sens:char:adis:stat {autodischarge_state};"
        return command

    def discharge_capacitor(self):
        """Discharges the capacitor.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "SYST:ZCH OFF"
        return command

    def stop_taking_data(self):
        """Stops taking measurements

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "ABOR"
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
        if read_option == enums.ReadingOption.LATEST:
            command = ":sens:data:latest?;"
        else:
            command = ":sens:data?;"
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

    def output_trigger_line(self, output_trigger_input):
        """Sets output trigger line

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":SENS:TOUT:SIGN {output_trigger_input:d};:SENS:TOUT:STAT ON;"
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
        command = f":trig:sour {enums.Source(source).name};"
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

    def set_infinite_triggers(self):
        """Return take infinite measurements

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trig:coun INF;"
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
        unit = enums.UnitMode(mode).name
        command = f":sens:{unit}:aper {time:f};"
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

        command = f":sens:func '{enums.UnitMode(mode).value}';"
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

    def start_storing_buffer(self):
        """Return start storing buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:feed:cont NEXT;"
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
            f"{self.format_trac()} "
            f"{self.set_buffer_size(50000)}"
        )
        return command

    def perform_zero_calibration(self, mode, auto, range_value, int_time):
        """Return combo of commands for perform zero calibration command.
        Required when setting mode to Volts/Amps to cancel any internal
        offsets. See page 4-10 in User's manual for sequence

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
            f"{self.enable_zero_check(enable=True)} "
            f"{self.set_mode(mode=mode)} "
            f"{self.set_range(auto=auto, range_value=range_value, mode=mode)} "
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

    def toggle_voltage_source(self, enable):
        command = ":vsou:oper ON;" if enable else ":vsou:oper OFF;"
        return command

    def get_voltage_source_status(self):
        command = ":vsou:oper?;"
        return command

    def get_voltage_level(self):
        command = ":sour:volt:lev:imm:ampl?;"
        return command

    def set_voltage_level(self, amplititude):
        command = f":sour:volt:lev:imm:ampl {amplititude};"
        return command

    def get_voltage_range(self):
        command = ":sour:volt:rang?;"
        return command

    def set_voltage_range(self, range):
        command = f":sour:volt:rang {range};"
        return command

    def get_voltage_limit(self):
        command = ":sour:volt:lim:stat?;"
        return command

    def set_voltage_limit(self, limit):
        command = f":sour:volt:lim:ampl {limit};"
        return command

    def set_resolution(self, mode, digit):
        command = f":sens:{enums.UnitMode(mode).value}:dig {digit};"
        return command


class KeithleyElectrometerCommandFactory(ElectrometerCommandFactory):
    """Class that formats commands to control the electrometer via RS-232."""

    def __init__(self) -> None:
        super().__init__()


class KeysightElectrometerCommandFactory(ElectrometerCommandFactory):
    """Class that formats commands to control the electrometer via RS-232."""

    def __init__(self) -> None:
        super().__init__()

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
        unit_ = enums.UnitMode(mode).name
        filter_name = enums.Filter(filter_type).name
        if filter_name == "AVER":
            command = f":sens:{unit_}:{filter_name}:mov:stat {int(active)};"
        else:
            command = f":sens:{unit_}:{filter_name}:stat {int(active)};"
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
        filter_name = enums.Filter(filter_type).name
        unit = enums.UnitMode(mode).name
        if enums.Filter(filter_type).name == "AVER":
            command = f":sens:{unit}:{filter_name}:mov:stat?;"
        else:
            command = f":sens:{unit}:{filter_name}:stat?;"
        return command

    def always_read(self) -> str:
        """Return always read buffer.

        Returns
        -------
        commmand : `str`
            The generated command string. An array of all data in the buffer.
        """
        command = ":trac:data?"
        return command

    def next_read(self):
        """Return the latest measurement data from buffer

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":meas:data?"
        return command

    def acquire_data(self):
        """Returns the command to start acquiring data

        Returns
        -------
        command : `str`
            The generated command string
        """
        command = ":init:acq"
        return command

    def get_last_error(self):
        """Return get last error.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":syst:err:next?;"
        return command

    def format_trac(
        self,
        timestamp=True,
        temperature=False,
        voltage=False,
        set_mode=False,
        mode="VOLT",
        channel=False,
    ):
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
        self.data_columns = 1
        if not (timestamp or temperature or voltage or set_mode):
            command = ":form:elem:sens NONE"
        else:
            command = ":form:elem:sens "
            if channel:
                isFirst = False
                command += "CHAN"
                self.data_columns += 1
            if timestamp:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "TIME"
                self.data_columns += 1
            if temperature:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "TEMP"
                self.data_columns += 1
            if voltage:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += "SOUR"
                self.data_columns += 1
            if set_mode:
                if not isFirst:
                    command += ", "
                isFirst = False
                command += f"{mode}"
                self.data_columns += 1
        command += ";"
        return command

    def get_trace_format(self):
        """Returns the format of the trace.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":form:elem:sens?"
        return command

    def discharge_capacitor(self):
        """Discharges the capacitor.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "SENS:CHAR:DISC"
        return command

    def stop_taking_data(self):
        """Stops taking measurements

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "ABOR:ACQ;"
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
            command = ":syst:temp ON;"
        else:
            command = ":syst:temp OFF;"
        return command

    def read_buffer(self):
        """Return read buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":sens:data?;"
        return command

    def output_trigger_line(self):
        """Sets output trigger line

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":TRIG:ACQ:TOUT ON;:TRIG:ACQ:TOUT:SIGN TOUT"
        return command

    def init_buffer(self):
        """Return start storing readings into the buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":init:acq;"
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
        command = f":sens:func:on '{enums.UnitMode(mode).name}';:inp on;"
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
        command = ":inp:zcor ON;" if enable else ":inp:zcor OFF;"
        return command

    def perform_zero_calibration(self, mode, auto, range_value, int_time):
        """Return combo of commands for perform zero calibration command.
        Required when setting mode to Volts/Amps to cancel any internal
        offsets. See page 4-10 in User's manual for sequence

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
            f"{self.set_mode(mode)}"
            f"{self.set_range(auto=auto, range_value=range_value, mode=mode)}"
            f"{self.integration_time(mode,int_time)}"
            f"{self.enable_zero_correction(enable=True)}"
        )
        return command

    def toggle_voltage_source(self, enable):
        command = (
            ":sens:res:man:vso:oper ON;" if enable else ":sens:res:man:vso:oper OFF;"
        )
        return command

    def get_voltage_source_status(self):
        command = ":sens:res:man:vso:oper?;"
        return command
