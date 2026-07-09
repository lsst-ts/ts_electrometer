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
    """Format SCPI commands common to supported electrometers."""

    def __init__(self):
        pass

    def activate_filter(self, mode, filter_type, active):
        """Build a command that enables or disables a digital filter.

        Parameters
        ----------
        mode : `str` or `enums.UnitMode`
            Measurement mode.
        filter_type : `int` or `enums.Filter`
            Filter type.
        active : `bool`
            Whether to enable the filter.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        unit = enums.UnitMode(mode).name
        filter = enums.Filter(filter_type).name
        return f":sens:{unit}:{filter}:stat {int(active)};"

    def get_filter_status(self, mode, filter_type):
        """Build a command that queries a digital filter status.

        Parameters
        ----------
        mode : `str` or `enums.UnitMode`
            Measurement mode.
        filter_type : `int` or `enums.Filter`
            Filter type.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        unit = enums.UnitMode(mode).name
        filter = enums.Filter(filter_type).name
        return f":sens:{unit}:{filter}:stat?;"

    def always_read(self) -> str:
        """Build a command that reads the full buffer continuously.

        Returns
        -------
        command : `str`
            Generated command string.
        """
        return f":trac:feed:cont alw;{self.init_buffer()}"

    def next_read(self):
        """Build a command that reads the next buffer sample.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        return f":trac:feed:cont NEXT;{self.init_buffer()}"

    def acquire_data(self):
        """Build a command that starts acquiring data.

        Returns
        -------
        command : `str`
            Generated command string.
        """
        return f":trac:feed:cont NEXT;{self.init_buffer()}"

    def clear_buffer(self):
        """Build a command that clears the buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:cle;"
        return command

    def clear_device(self):
        """Build a command that clears the device.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "^C"
        return command

    def get_last_error(self):
        """Build a command that queries the last error.

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
        """Build a command that configures the trace buffer format.

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
        """Build a command that queries the trace format.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:elem?;"
        return command

    def get_buffer_quantity(self):
        """Build a command that queries the number of buffered samples.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = ":trac:poin:act?;"
        return command

    def get_hardware_info(self):
        """Build a command that queries the hardware identification string.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "*idn?;"
        return command

    def set_autodischarge(self, autodischarge_state):
        """Build a command that sets the autodischarge state.

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
        """Return a command to select the trigger source.

        Parameters
        ----------
        source : `enums.Source`, optional
            Trigger source.

        Returns
        -------
        command : `str`
            The generated command string.
        """
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
            The unit of the aperture to set.
        time : `float`, optional
            The integration time of the aperture. Defaults to 0.001 seconds.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        unit = enums.UnitMode(mode).name
        command = f":sens:{unit}:aper {time:f};"
        return command

    def auto_integration_time_on(self, mode):
        """Return a command to enable automatic integration time.

        Parameters
        ----------
        mode : `str` or `enums.UnitMode`
            Measurement mode.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        unit = enums.UnitMode(mode).name
        command = f":sens:{unit}:aper:auto ON;"
        return command

    def auto_nplc_on(self, mode):
        """Turn on auto NPLC.

        Parameters
        ----------
        mode : UnitMode
            The unit to change setting.

        Returns
        -------
        command: `str`
            The formatted command.
        """
        unit = enums.UnitMode(mode).name
        command = f":sens:{unit}:nplc:auto ON;"
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
            command = ":sens:" + enums.UnitMode(mode).name + ":rang:auto ON;"
        else:
            command = ":sens:" + enums.UnitMode(mode).name + ":rang:auto OFF;"
            command += "\n:sens:" + enums.UnitMode(mode).name + ":rang " + str(range_value) + ";"
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

    def set_timer(self, mode, value):
        """Return set time command string.

        Parameters
        ----------
        mode : `str` or `enums.UnitMode`
            Measurement mode.
        value : `float`
            Timer value in power-line cycles.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).lower()}:nplc {value};"
        return command

    def get_timer(self, mode):
        """Return the get nplc command.

        Parameters
        ----------
        mode : `str`
            The name of the mode to set the nplc for.
        """
        return f":sens:{enums.UnitMode(mode).lower()}:nplc?;"

    def prepare_buffer(self):
        """Return combo of commands for prepare buffer command.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f"{self.clear_buffer()} {self.format_trac()} {self.set_buffer_size(50000)}"
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
        int_time : `float`
            Integration time to use for the calibration.

        Returns
        -------
        command : `str`
            The generated command string
        """
        command = (
            f"{self.enable_zero_check(enable=True)} "
            f"{self.set_mode(mode=mode)} "
            f"{self.set_range(auto=auto, range_value=range_value, mode=mode)} "
            f"{self.enable_zero_check(enable=False)} "
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
        """Return a command to enable or disable the voltage source.

        Parameters
        ----------
        enable : `bool`
            Whether to enable the voltage source.
        """
        command = ":vsou:oper ON;" if enable else ":vsou:oper OFF;"
        return command

    def get_voltage_source_status(self):
        """Return a command to query voltage source status."""
        command = ":vsou:oper?;"
        return command

    def get_voltage_level(self):
        """Return a command to query voltage source level."""
        command = ":sour:volt:lev:imm:ampl?;"
        return command

    def set_voltage_level(self, amplititude):
        """Return a command to set voltage source level.

        Parameters
        ----------
        amplititude : `float`
            Voltage level to set.
        """
        command = f":sour:volt:lev:imm:ampl {amplititude};"
        return command

    def get_voltage_range(self):
        """Return a command to query voltage source range."""
        command = ":sour:volt:rang?;"
        return command

    def set_voltage_range(self, range):
        """Return a command to set voltage source range.

        Parameters
        ----------
        range : `float`
            Voltage range to set.
        """
        command = f":sour:volt:rang {range};"
        return command

    def get_voltage_limit(self):
        """Return a command to query voltage source limit."""
        command = ":sour:volt:lim:stat?;"
        return command

    def set_voltage_limit(self, limit):
        """Return a command to set voltage source limit.

        Parameters
        ----------
        limit : `float`
            Voltage limit to set.
        """
        command = f":sour:volt:lim:ampl {limit};"
        return command

    def set_resolution(self, mode, digit):
        """Return a command to set measurement resolution.

        Parameters
        ----------
        mode : `str` or `enums.UnitMode`
            Measurement mode.
        digit : `int`
            Number of resolution digits.
        """
        command = f":sens:{enums.UnitMode(mode).value}:dig {digit};"
        return command

    def clear(self):
        """Return a command to clear device status."""
        return "*CLS;"


class KeithleyElectrometerCommandFactory(ElectrometerCommandFactory):
    """Format Keithley-specific SCPI commands for RS-232 control."""

    def __init__(self) -> None:
        super().__init__()


class KeysightElectrometerCommandFactory(ElectrometerCommandFactory):
    """Format Keysight-specific SCPI commands for RS-232 control.

    This class includes commands that differ from the Keithley command set.
    """

    def __init__(self) -> None:
        super().__init__()

    def perform_zero_calibration(self, mode, auto, range_value, int_time):
        """Build the command sequence for zero calibration.

        Required when setting mode to volts or amps to cancel internal
        offsets. See page 4-10 of the user manual for the sequence.

        Parameters
        ----------
        mode : `UnitMode`
            Measurement unit for the device.
        auto : `bool`
            Whether auto range is activated.
        range_value : `float`
            The range of the values.
        int_time : `float`
            Integration time to use for the calibration.

        Returns
        -------
        command : `str`
            Generated command string.
        """
        command = (
            f"{self.set_mode(mode=mode)} {self.set_range(auto=auto, range_value=range_value, mode=mode)} "
        )
        return command

    def activate_filter(self, mode, filter_type, active) -> str:
        """Build a command that enables or disables a digital filter.

        Parameters
        ----------
        mode : `UnitMode`
            Measurement unit for the filter to activate.
        filter_type : `Filter`
            Filter type to activate.
        active : `int`
            Whether to activate the filter.

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
            if unit_ == "CURR":
                command = f":sens:{unit_}:{filter_name}:stat {int(active)};"
            else:
                # cannot set filter type
                return "0"
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
            if unit == "CURR":
                command = f":sens:{unit}:{filter_name}:stat?;"
        return command

    def always_read(self) -> str:
        """Return always read buffer.

        Returns
        -------
        command : `str`
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
        timestamp : `bool`
            Whether to store timestamp data.
        temperature : `bool`
            Whether to store temperature data.
        voltage : `bool`
            Whether to store voltage-source data.
        set_mode : `bool`
            Whether to store data for a specified measurement mode.
        mode : `str`
            Measurement mode to store when ``set_mode`` is true.
        channel : `bool`
            Whether to store channel data.

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
        command = ":form:elem:sens?;"
        return command

    def discharge_capacitor(self):
        """Discharges the capacitor.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "SENS:CHAR:DISC;"
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
        command = ":TRIG:ACQ:TOUT ON;:TRIG:ACQ:TOUT:SIGN TOUT;"
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

    def toggle_voltage_source(self, enable):
        """Return a command to enable or disable the voltage source."""
        command = ":sens:res:man:vso:oper ON;" if enable else ":sens:res:man:vso:oper OFF;"
        return command

    def get_voltage_source_status(self):
        """Return a command to query voltage source status."""
        command = ":sens:res:man:vso:oper?;"
        return command

    def clear_array(self):
        """Return clear buffer.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = "sens:data:cle;"
        return command

    def integration_time(self, mode, time=0.001):
        """Return integration time.

        Parameters
        ----------
        mode : `UnitMode`
            The unit of the aperture to set.
        time : `float`, optional
            The integration time of the aperture. Defaults to 0.001 seconds.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        unit = enums.UnitMode(mode).name
        command = f":sens:{unit}:aper {time:f};:trig:acq:tim {time:f};"
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

    def set_timer(self, mode, value):
        """Return set time command string.

        Parameters
        ----------
        mode : `str` or `enums.UnitMode`
            Measurement mode.
        value : `float`
            Timer value in power-line cycles.

        Returns
        -------
        command : `str`
            The generated command string.
        """
        command = f":sens:{enums.UnitMode(mode).lower()}:nplc {value};:trig:acq:tim {value / 50:f};"
        return command
