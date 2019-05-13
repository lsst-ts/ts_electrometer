from enum import Enum


class ElectrometerCommand:
    """Class that contains low level commands to control the electrometer via RS-232
    """
    def __init__(self):
        self.device = TestDevice()

    def activateFilter(self, mode, filterType, active):
        """Activate/deactivate a type of filter

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            filterType {filterType enum} -- MED = 1, AVER = 2
            active {bool} -- Boolean to activate or de-activate the filter

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:"
        command += mode.name + ":" + filterType.name + ":STAT "
        command += "1" if active else "0"
        command += ";"
        return command

    def getAvgFilterStatus(self, mode):
        """Get the type of average filter the device is using

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:"
        command += mode.name
        command += ":AVER:TYPE?;"
        return command

    def getMedFilterStatus(self, mode):
        """Get the type of median filter the device is using

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:"
        command += mode.name
        command += ":MED:STAT?;"
        return command

    def getFilterStatus(self, mode, filterType):
        """Get filter status

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            filterType {filterType enum} -- MED = 1, AVER = 2

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:"
        command += mode.name + ":"
        command += filterType.name
        command += ":STAT?;"
        return command

    def setAvgFilterStatus(self, mode, averFilterType):
        """Set the type of average filter to set

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            averFilterType {AverFilterType enum} -- NONE = 1, SCAL = 2, ADV = 3

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:"
        command += mode.name
        command += ":AVER:TYPE "
        command += averFilterType.name + ";"
        return command

    def setMedFilterStatus(self, mode, active):
        """Set the type of median filter to set

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4
            active {bool} -- Boolean to activate or de-activate the filter

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:"
        command += mode.name
        command += ":MED:STAT "
        command += "1" if active else "0"
        command += ";"
        return command

    def alwaysRead(self):
        """Always read value a store them into the buffer

        Returns:
            string -- string with the low level command command
        """
        command = ":TRAC:FEED:CONT ALW;"
        command += "\n:INIT;"
        return command

    def nextRead(self):
        """Read value a store them into the buffer until the buffer is full

        Returns:
            string -- string with the low level command command
        """
        command = ":TRAC:FEED:CONT NEXT;"
        command += "\n:INIT;"
        return command

    def clearBuffer(self):
        """Clear device buffer

        Returns:
            string -- string with the low level command command
        """
        command = ":TRAC:CLE;"
        return command

    def clearDevice(self):
        """Clear device buffer

        Returns:
            string -- string with the low level command command
        """
        command = "^C"
        return command

    def getLastError(self):
        """Get error query

        Returns:
            string -- string with the low level command command
        """
        command = ":SYST:ERR?;"
        return command

    def formatTrac(self, channel, timestamp, temperature):
        """Format the reads to include or remove values from input

        Arguments:
            channel {bool} -- Boolean to include or exclude the channel from the reading
            timestamp {bool} -- Boolean to include or exclude the teimestamp from the reading
            temperature {bool} -- Boolean to include or exclude the tempearture from the reading

        Returns:
            string -- string with the low level command command
        """
        isFirst = True
        if(not (timestamp or temperature or channel)):
            command = ":TRAC:ELEM NONE"
        else:
            command = ":TRAC:ELEM "
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

    def getBufferQuantity(self):
        """Get the quantity of values stored in the buffer

        Returns:
            string -- string with the low level command command
        """
        command = ":TRAC:POIN:ACT?;"
        return command

    def getHardwareInfo(self):
        """Get hardware info

        Returns:
            string -- string with the low level command command
        """
        command = "*IDN?"
        return command

    def getMeasure(self, readOption):
        """Get measurement from the electrometer

        Arguments:
            readOption {readingOption enum} -- Type of reading,  LATEST = 1  for last value read, NEWREAD = 2
            for new reading

        Returns:
            string -- string with the low level command command
        """
        if(readOption == readingOption.LATEST):
            command = ":SENS:DATA?;"
        else:
            command = ":SENS:DATA:FRES?;"
        return command

    def getMode(self):
        """Get the mode the Electrometer is using

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:FUNC?;"
        return command

    def enableTemperatureReading(self, enable):
        """Enable temperature readings. Enabling temperature readings will reduce the ammount of readings
        the electrometer can handle

        Arguments:
            enable {bool} -- Boolean to activate or de-activate temperature readings

        Returns:
            string -- string with the low level command command
        """
        if(enable):
            command = ":SYST:TSC ON;"
        else:
            command = ":SYST:TSC OFF;"
        return command

    def readBuffer(self):
        """Command to read the buffer, don't read all in one read.
        Split in a small ammount of byte (256)

        Returns:
            string -- string with the low level command command
        """
        command = ":TRAC:DATA?;"
        return command

    def resetDevice(self):
        """Clean the elecrometer configuration to factory settings

        Returns:
            string -- string with the low level command command
        """
        command = "*RST;\n:TRACE:CLEAR;"
        return command

    def selectDeviceTimer(self, timer=0.001):
        """Update the Internal processing loop of the electrometer, the fastest
        the more process the electrometer can handle

        Keyword Arguments:
            timer {float} -- Internal processing loop in the electrometer (default: {0.001})

        Returns:
            string -- string with the low level command command
        """
        command = ":TRIG:SOUR TIM;\n:TRIG:TIM " + '{0:.3f}'.format(timer) + ";"
        return command

    def setBufferSize(self, bufferSize=50000):
        """Set the buffer size of the electrometer. The maximum is 50000 (Also default value)

        Keyword Arguments:
            bufferSize {int} -- Maximum number of readings the buffer can store (default: {50000})

        Returns:
            string -- string with the low level command command
        """
        command = ":TRACE:CLEAR;\n:TRAC:POINTS " + str(bufferSize) + ";\n:TRIG:COUNT " + str(bufferSize) + ";"
        return command

    def initBuffer(self):
        """Initialize the buffer readings recording

        Returns:
            string -- string with the low level command command
        """
        command = ":INIT;"
        return command

    def integrationTime(self, mode, time=0.001):
        """Update the integration time in the electrometer

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Keyword Arguments:
            time {float} -- Integration rate in seconds (166.67e-6 to 200e-3) (default: {0.001})

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:" + mode.name + ":APER " + str(time) + ";"
        return command

    def setMode(self, mode):
        """Select measurement function: ‘VOLTage[:DC]’, ‘CURRent[:DC]’, ‘RESistance’, ‘CHARge’

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:FUNC '" + mode.name + "';"
        return command

    def setRange(self, auto, rangeValue, mode):
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
            command = ":SENS:" + mode.name + ":RANG:AUTO 1;"
        else:
            command = ":SENS:" + mode.name + ":RANG:AUTO 0;"
            command += "\n:SENS:" + mode.name + ":RANG " + str(rangeValue) + ";"
        return command

    def enableSync(self, enable):
        """This command is used to enable or disable line synchronization. When enabled,
        the integration period will not start until the beginning of the next power line cycle
        Arguments:
            enable {bool} -- Boolean to enable or disable synchronization

        Returns:
            string -- string with the low level command command
        """
        command = ":SYSTEM:LSYN:STAT ON;" if enable else ":SYSTEM:LSYN:STAT OFF;"
        return command

    def stopReadingBuffer(self):
        """Stop storing readings in the buffer. If this is not used,
        the electrometer can hang while reading data inside the buffer

        Returns:
            string -- string with the low level command command
        """
        command = ":TRAC:FEED:CONT NEV;"
        return command

    def enableAllInstrumentErrors(self):
        """Enable instrument errors in the electrometer.

        Returns:
            string -- string with the low level command command
        """
        command = ":STAT:QUE:ENAB (-440:+958);"
        return command

    def enableZeroCheck(self, enable):
        """When zero check is enabled (on), the input amplifier is reconfigured to
        shunt the input signal to low

        Arguments:
            enable {bool} -- Activate zero check

        Returns:
            string -- string with the low level command command
        """
        command = ":SYST:ZCH ON;" if enable else ":SYST:ZCH OFF;"
        return command

    def enableZeroCorrection(self, enable):
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
        command = ":SYST:ZCOR ON;" if enable else ":SYST:ZCOR OFF;"
        return command

    def getRange(self, mode):
        """Get current range currently configured for a specific mdoe

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:" + mode.name + ":RANG?;"
        return command

    def getIntegrationTime(self, mode):
        """Get integration time currently configured for a specific mdoe

        Arguments:
            mode {UnitMode enum} -- CURR = 1, CHAR = 2, VOLT = 3, RES = 4

        Returns:
            string -- string with the low level command command
        """
        command = ":SENS:" + mode.name + ":APER?;"
        return command

    def enableDisplay(self, enable):
        """Activate or de-activate the display on the electrometer. Using
        the display use process on the device, that's why it's usually disabled

        Arguments:
            enable {bool} -- Enable or disable the display

        Returns:
            string -- string with the low level command command
        """
        command = ":DISP:ENAB ON;" if enable else ":DISP:ENAB OFF;"
        return command

    def setTimer(self):
        """Set the timer in the electrometer to 0.01

        Returns:
            string -- string with the low level command command
        """
        command = ":SENSE:CURR:NPLC 0.01;"
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


class readingOption(Enum):
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

    def connect(self):
        self.connected = False

    def isConnected(self):
        return self.connected

    def getMessage(self):
        print(self.messageReceived)
        return self.messageReceived

    def sendMessage(self, message):
        print(self.messageToSend + message)
        return message
