from enum import Enum


class ElectrometerCommand:

    def __init__(self):
        self.device = TestDevice()

    def activateFilter(self, mode, filterType, active):
        """Activate/deactivate a type of filter

        Arguments:
            mode {[type]} -- [description]
            filterType {[type]} -- [description]
            active {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:"
        command += mode.name + ":" + filterType.name + ":STAT "
        command += "1" if active else "0"
        command += ";"
        return command

    def getAvgFilterStatus(self, mode):
        """Get the type of average filter the device is using

        Arguments:
            mode {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:"
        command += mode.name
        command += ":AVER:TYPE?;"
        return command

    def getMedFilterStatus(self, mode):
        """Get the type of median filter the device is using

        Arguments:
            mode {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:"
        command += mode.name
        command += ":MED:STAT?;"
        return command

    def getFilterStatus(self, mode, filterType):
        """Get filter status

        Arguments:
            mode {[type]} -- [description]
            filterType {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:"
        command += mode.name + ":"
        command += filterType.name
        command += ":STAT?;"
        return command

    def setAvgFilterStatus(self, mode, averFilterType):
        """Set the type of average filter to set

        Arguments:
            mode {[type]} -- [description]
            averFilterType {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:"
        command += mode.name
        command += ":AVER:TYPE "
        command += averFilterType.name + ";"
        return command

    def setMedFilterStatus(self, mode, active):
        """Set the type of median filter to set

        Arguments:
            mode {[type]} -- [description]
            active {[type]} -- [description]

        Returns:
            [type] -- [description]
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
            [type] -- [description]
        """
        command = ":TRAC:FEED:CONT ALW;"
        command += "\n:INIT;"
        return command

    def nextRead(self):
        """Read value a store them into the buffer until the buffer is full

        Returns:
            [type] -- [description]
        """
        command = ":TRAC:FEED:CONT NEXT;"
        command += "\n:INIT;"
        return command

    def clearBuffer(self):
        """Clear device buffer

        Returns:
            [type] -- [description]
        """
        command = ":TRAC:CLE;"
        return command

    def clearDevice(self):
        """Clear device buffer

        Returns:
            [type] -- [description]
        """
        command = "^C"
        return command

    def getLastError(self):
        """Get error query

        Returns:
            [type] -- [description]
        """
        command = ":SYST:ERR?;"
        return command

    def formatTrac(self, channel, timestamp, temperature):
        """Format the reads to include values from input

        Arguments:
            channel {[type]} -- [description]
            timestamp {[type]} -- [description]
            temperature {[type]} -- [description]

        Returns:
            [type] -- [description]
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
            [type] -- [description]
        """
        command = ":TRAC:POIN:ACT?;"
        return command

    def getHardwareInfo(self):
        """Get hardware info

        Returns:
            [type] -- [description]
        """
        command = "*IDN?"
        return command

    def getMeasure(self, readOption):
        """[summary]

        Arguments:
            readOption {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        if(readOption == readingOption.LATEST):
            command = ":SENS:DATA?;"
        else:
            command = ":SENS:DATA:FRES?;"
        return command

    def getMode(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:FUNC?;"
        return command

    def enableTemperatureReading(self, enable):
        if(enable):
            command = ":SYST:TSC ON;"
        else:
            command = ":SYST:TSC OFF;"
        return command

    def readBuffer(self):
        """Command to read the buffer, don't read all in one read. 
        Split in a small ammount of byte (256)

        Returns:
            [type] -- [description]
        """
        command = ":TRAC:DATA?;"
        return command

    def resetDevice(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        command = "*RST;\n:TRACE:CLEAR;"
        return command

    def selectDeviceTimer(self, timer=0.001):
        """[summary]

        Keyword Arguments:
            timer {float} -- [description] (default: {0.001})

        Returns:
            [type] -- [description]
        """
        command = ":TRIG:SOUR TIM;\n:TRIG:TIM " + '{0:.3f}'.format(timer) + ";"
        return command

    def setBufferSize(self, bufferSize=50000):
        """[summary]

        Keyword Arguments:
            bufferSize {int} -- [description] (default: {50000})

        Returns:
            [type] -- [description]
        """
        command = ":TRACE:CLEAR;\n:TRAC:POINTS " + str(bufferSize) + ";\n:TRIG:COUNT " + str(bufferSize) + ";"
        return command

    def initBuffer(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        command = ":INIT;"
        return command

    def integrationTime(self, mode, time=0.001):
        """[summary]

        Arguments:
            mode {[type]} -- [description]

        Keyword Arguments:
            time {float} -- [description] (default: {0.001})

        Returns:
            [type] -- [description]
        """
        command = ":SENS:" + mode.name + ":APER " + str(time) + ";"
        return command

    def setMode(self, mode):
        """[summary]

        Arguments:
            mode {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:FUNC '" + mode.name + "';"
        return command

    def setRange(self, auto, rangeValue, mode):
        """[summary]

        Arguments:
            auto {[type]} -- [description]
            rangeValue {[type]} -- [description]
            mode {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        if(auto):
            command = ":SENS:" + mode.name + ":RANG:AUTO 1;"
        else:
            command = ":SENS:" + mode.name + ":RANG:AUTO 0;"
            command += "\n:SENS:" + mode.name + ":RANG " + str(rangeValue) + ";"
        return command

    def enableSync(self, enable):
        """[summary]

        Arguments:
            enable {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SYSTEM:LSYN:STAT ON;" if enable else ":SYSTEM:LSYN:STAT OFF;"
        return command

    def stopReadingBuffer(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        command = ":TRAC:FEED:CONT NEV;"
        return command

    def enableAllInstrumentErrors(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        command = ":STAT:QUE:ENAB (-440:+958);"
        return command

    def enableZeroCheck(self, enable):
        """[summary]

        Arguments:
            enable {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SYST:ZCH ON;" if enable else ":SYST:ZCH OFF;"
        return command

    def enableZeroCorrection(self, enable):
        """[summary]

        Arguments:
            enable {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SYST:ZCOR ON;" if enable else ":SYST:ZCOR OFF;"
        return command

    def getRange(self, mode):
        """[summary]

        Arguments:
            mode {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:" + mode.name + ":RANG?;"
        return command

    def getIntegrationTime(self, mode):
        """[summary]

        Arguments:
            mode {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SENS:" + mode.name + ":APER?;"
        return command

    def enableDisplay(self, enable):
        """[summary]

        Arguments:
            enable {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":DISP:ENAB ON;" if enable else ":DISP:ENAB OFF;"
        return command

    def enableSync(self, enable):
        """[summary]

        Arguments:
            enable {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        command = ":SYSTEM:LSYNC:STAT ON;" if enable else ":SYSTEM:LSYNC:STAT OFF;"
        return command

    def setTimerTest(self):
        """[summary]

        Returns:
            [type] -- [description]
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