from enum import Enum


class ElectrometerCommand:
    """Class that contains low level commands to control the electrometer via RS-232
    """
    def __init__(self):
        self.device = TestDevice()

    def activate_filter(self, mode, filter_type, active):
        """Activate/deactivate a type of filter

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            filterType {filterType enum} -- MED = 1, AVER = 2
            active {bool} -- Boolean to activate or de-activate the filter

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:{UnitMode(mode).name}:{Filter(filter_type).name}:stat {int(active)};"
        return command

    def get_avg_filter_status(self, mode):
        """Get the type of average filter the device is using

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:{UnitMode(mode).name}:aver:type?;"
        return command

    def get_med_filter_status(self, mode):
        """Get the type of median filter the device is using

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:{UnitMode(mode).name}:med:stat?;"
        return command

    def get_filter_status(self, mode, filter_type):
        """Get filter status

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            filterType {filterType enum} -- MED = 1, AVER = 2

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:{UnitMode(mode).name}:{Filter(filter_type).name}:stat?"
        return command

    def set_avg_filter_status(self, mode, aver_filter_type):
        """Set the type of average filter to set

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            averFilterType {AverFilterType enum} -- NONE = 1, SCAL = 2, ADV = 3

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:{UnitMode(mode).name}:aver:type {AverFilterType(aver_filter_type).name};"
        return command

    def set_med_filter_status(self, mode, active):
        """Set the type of median filter to set

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            active {bool} -- Boolean to activate or de-activate the filter

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:{UnitMode(mode).name}:med:stat {int(active)};"
        return command

    def always_read(self):
        """Always read value and store them into the buffer

        Returns:
            string -- string with the low level command command
        """
        command = f":trac:feed:cont alw;{self.init_buffer()}"
        return command

    def next_read(self):
        """Read value and store them into the buffer until the buffer is full

        Returns:
            string -- string with the low level command command
        """
        command = f":trac:feed:cont next;{self.init_buffer()}"
        return command

    def clear_buffer(self):
        """Clear device buffer

        Returns:
            string -- string with the low level command command
        """
        command = ":trac:cle;"
        return command

    def clear_device(self):
        """Clear device buffer

        Returns:
            string -- string with the low level command command
        """
        command = "^C"
        return command

    def get_last_error(self):
        """Get error query

        Returns:
            string -- string with the low level command command
        """
        command = ":syst:err?;"
        return command

    def format_trac(self, channel=False, timestamp=True, temperature=False):
        """Format the reads to include or remove values from input

        Arguments:
            channel {bool} -- Boolean to include or exclude the channel from the reading
            timestamp {bool} -- Boolean to include or exclude the timestamp from the reading
            temperature {bool} -- Boolean to include or exclude the temperature from the reading

        Returns:
            string -- string with the low level command command
        """
        isFirst = True
        if(not (timestamp or temperature or channel)):
            command = ":trac:elem NONE"
        else:
            command = ":trac:elem "
            if (channel):
                isFirst = False
                command += "CHAN"
            if(timestamp):
                if (not isFirst):
                    command += ", "
                isFirst = False
                command += "TST"
            if (temperature):
                if (not isFirst):
                    command += ", "
                isFirst = False
                command += "ETEM"
        command += ";"
        return command

    def get_buffer_quantity(self):
        """Get the quantity of values stored in the buffer

        Returns:
            string -- string with the low level command command
        """
        command = ":trac:poin:act?;"
        return command

    def get_hardware_info(self):
        """Get hardware info

        Returns:
            string -- string with the low level command command
        """
        command = "*idn?"
        return command

    def get_measure(self, read_option):
        """Get measurement from the electrometer

        Arguments:
            readOption {readingOption enum} -- Type of reading,  LATEST = 1  for last value read, NEWREAD = 2
            for new reading

        Returns:
            string -- string with the low level command command
        """
        if (ReadingOption(read_option) == ReadingOption.LATEST):
            command = ":sens:data?;"
        else:
            command = ":sens:data:fres?;"
        return command

    def get_mode(self):
        """Get the mode the Electrometer is using

        Returns:
            string -- string with the low level command command
        """
        command = ":sens:func?;"
        return command

    def enable_temperature_reading(self, enable):
        """Enable temperature readings. Enabling temperature readings will reduce the ammount of readings
        the electrometer can handle

        Arguments:
            enable {bool} -- Boolean to activate or de-activate temperature readings

        Returns:
            string -- string with the low level command command
        """
        if(enable):
            command = ":syst:tsc ON;"
        else:
            command = ":syst:tsc OFF;"
        return command

    def read_buffer(self):
        """Command to read the buffer, don't read all in one read.
        Split in a small ammount of byte (256)

        Returns:
            string -- string with the low level command command
        """
        command = ":trac:data?;"
        return command

    def reset_device(self):
        """Clean the elecrometer configuration to factory settings

        Returns:
            string -- string with the low level command command
        """
        command = f"*RST; {self.clear_buffer()}"
        return command

    def select_device_timer(self, timer=0.001):
        """Update the Internal processing loop of the electrometer, the fastest
        the more process the electrometer can handle

        Keyword Arguments:
            timer {float} -- Internal processing loop in the electrometer (default: {0.001})

        Returns:
            string -- string with the low level command command
        """
        command = f":trig:sour tim;\n:trig:tim {timer:.3f};"
        return command

    def set_buffer_size(self, buffer_size=50000):
        """Set the buffer size of the electrometer. The maximum is 50000 (Also default value)

        Keyword Arguments:
            bufferSize {int} -- Maximum number of readings the buffer can store (default: {50000})

        Returns:
            string -- string with the low level command command
        """
        command = f"{self.clear_buffer()}:trac:points {str(buffer_size)};:trig:count {str(buffer_size)};"
        return command

    def init_buffer(self):
        """Initialize the buffer readings recording

        Returns:
            string -- string with the low level command command
        """
        command = ":init;"
        return command

    def integration_time(self, mode, time=0.001):
        """Update the integration time in the electrometer

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Keyword Arguments:
            time {float} -- Integration rate in seconds (166.67e-6 to 200e-3) (default: {0.001})

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:{UnitMode(mode).name}:aper {str(time)};"
        return command

    def set_mode(self, mode):
        """Select measurement function: ‘VOLTage[:DC]’, ‘CURRent[:DC]’, ‘RESistance’, ‘CHARge’

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = f":sens:func '{UnitMode(mode).name}';"
        return command

    def set_range(self, auto, range_value, mode):
        """
        Arguments:
            auto {bool} -- The AUTO-RANGE option is used to configure autorange for the amps function.
            This option allows you to speed up the autoranging search process by eliminating upper
            and lower measurement ranges
            rangeValue {float} -- This command is used to manually select the measurement range for the
            specified measurement function. The range is selected by specifying the expected
            reading as an absolute value. If auto is ON, this parameter is ommited.
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        if(auto):
            command = ":sens:" + UnitMode(mode).name + ":rang:auto 1;"
        else:
            command = ":sens:" + UnitMode(mode).name + ":rang:auto 0;"
            command += "\n:sens:" + UnitMode(mode).name + ":rang " + str(range_value) + ";"
        return command

    def enable_sync(self, enable):
        """This command is used to enable or disable line synchronization. When enabled,
        the integration period will not start until the beginning of the next power line cycle
        Arguments:
            enable {bool} -- Boolean to enable or disable synchronization

        Returns:
            string -- string with the low level command command
        """
        command = ":syst:lsyn:stat ON;" if enable else ":syst:lsyn:stat OFF;"
        return command

    def stop_storing_buffer(self):
        """Stop storing readings in the buffer. If this is not used,
        the electrometer can hang while reading data inside the buffer

        Returns:
            string -- string with the low level command command
        """
        command = ":trac:feed:cont NEV;"
        return command

    def enable_all_instrument_errors(self):
        """Enable instrument errors in the electrometer.

        Returns:
            string -- string with the low level command command
        """
        command = ":stat:que:enab (-440:+958);"
        return command

    def enable_zero_check(self, enable):
        """When zero check is enabled (on), the input amplifier is reconfigured to
        shunt the input signal to low

        Arguments:
            enable {bool} -- Activate zero check

        Returns:
            string -- string with the low level command command
        """
        command = ":syst:zch ON;" if enable else ":syst:zch OFF;"
        return command

    def enable_zero_correction(self, enable):
        """The Z-CHK and REL keys work together to cancel (zero correct) any internal offsets that might
        upset accuracy for volts and amps measurements.
        Perform the following steps to zero correct the volts or amps function:
        1. Select the V or I function.
        2. Press Z-CHK to enable Zero Check.
        3. Select the range that will be used for the measurement.
        4. Press REL to zero correct the instrument (REL indicator will be lit and “Zcor” displayed).
        Note that for the volts function, the “Zcor” message will not be displayed if guard was
        already enabled (“Grd” displayed).
        5. Press Z-CHK to disable zero check.
        6. Readings can now be taken in the normal manner.

        Arguments:
            enable {bool} -- Enable or disable zero correction in the electrometer

        Returns:
            string -- string with the low level command command
        """
        command = ":syst:zcor ON;" if enable else ":syst:zcor OFF;"
        return command

    def get_range(self, mode):
        """Get current range currently configured for a specific mdoe

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = ":sens:" + UnitMode(mode).name + ":rang?;"
        return command

    def get_integration_time(self, mode):
        """Get integration time currently configured for a specific mdoe

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = ":sens:" + UnitMode(mode).name + ":aper?;"
        return command

    def enable_display(self, enable):
        """Activate or de-activate the display on the electrometer. Using
        the display use process on the device, that's why it's usually disabled

        Arguments:
            enable {bool} -- Enable or disable the display

        Returns:
            string -- string with the low level command command
        """
        command = ":disp:enab ON;" if enable is True else ":disp:enab OFF;"
        return command

    def set_timer(self):
        """Set the timer in the electrometer to 0.01

        Returns:
            string -- string with the low level command command
        """
        command = ":sens:curr:nplc 0.01;"
        return command

    def prepare_buffer(self):
        command = f"{self.clear_buffer()} {self.format_trac(False, True, False)} {self.set_buffer_size(50000)}"
        return command

    def perform_zero_calibration(self, mode, auto, range_value):
        command = f"{self.enable_zero_check(True)} {self.set_mode(mode)} {self.set_range(auto=auto, range_value=range_value, mode=mode)} {self.enable_zero_correction(enable=True)} {self.enable_zero_check(False)}"
        return command

    def disable_all(self):
        command = f"{self.enable_sync(False)} :trig:del 0.0;"
        return command


class UnitMode(Enum):
    CURR = 1
    CHAR = 2
    VOLT = 3
    RES = 4


class Filter(Enum):
    MED = 1
    AVER = 2


class AverFilterType(Enum):
    NONE = 1
    SCAL = 2
    ADV = 3


class ReadingOption(Enum):
    LATEST = 1  # Last value read
    NEWREAD = 2  # New reading


class TestDevice:
    """Class used only for testing communication
    """

    def __init__(self):
        self.messageReceived = "getMessage executed..."
        self.messageToSend = "sendMessage executed: "
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def isConnected(self):
        return self.connected

    def getMessage(self):
        print(self.messageReceived)
        return self.messageReceived

    def sendMessage(self, message):
        print(self.messageToSend + message)
        return message
