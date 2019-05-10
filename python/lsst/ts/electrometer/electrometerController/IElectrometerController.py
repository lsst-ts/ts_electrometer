from abc import ABC, abstractmethod
from enum import Enum
from inspect import currentframe


class IElectrometerController(ABC):

    def __init__(self):
        self.state = self.ElectrometerStates.OFFLINESTATE

    @abstractmethod
    def connect(self):
        """Connects to the communication protocol port
        """
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the communication protocol
        """
        pass

    @abstractmethod
    def isConnected(self):
        """Check is the communication is active
        """
        pass

    @abstractmethod
    def performZeroCorrection(self):
        """Performs a zero correction in the device. It's recommended to perform this 
        zero correction every time the range changes. The steps taken to perform this 
        comes from the datasheet 6517B-901-01 Rev. B / June 2009 under Zero correct. 
        It is as following. 
        1- Enable Zero check, 
        2- Set unit to read, 
        3- Set range to measure,
        4- Enable Zero Correction,
        5- Disable Zero check. For unit and range, it uses the last values selected, 
        either via command or from the configuration file
        """
        pass

    @abstractmethod
    def readDuringTime(self, time):
        """Start storing readings inside the electrometer buffer for a fixed time, 
        this command will change detailedState from NotReadingState to 
        SetDurationReadingState and to stop storing data into the buffer and publish 
        the LFO there are 2 possibilities. Reading during scanDuration time input in 
        the command or sending a stopScan command
        
        Arguments:
            time {float} -- Time in seconds from the start of the reading until the 
            stop and then store into the FITS file. The start of the scan will take 
            about 0.2seconds which is what the device takes to start the reading 
            process
        """
        pass

    @abstractmethod
    def readManual(self):
        """Start storing readings inside the electrometer buffer, this command will 
        change detailedState from NotReadingState to ManualReadingState and continues 
        storing data into the buffer. The data will be published to the LFO when 
        stopScan command is received or a timeout occurs (300 seconds)
        """
        pass

    @abstractmethod
    def stopReading(self):
        """Command to stop a current reading process, when it finishes stopping the 
        process it will read the data from the buffer and will publish the LFO event
        """
        pass

    @abstractmethod
    def updateState(self, newState):
        """Update the detailedState of the electrometer controller

        Arguments:
            newState {Enum ElectrometerStates} -- Detailed state enumeration
            DISABLEDSTATE: Same as for SummaryState
            ENABLEDSTATE: Same as for SummaryState
            FAULTSTATE: Same as for SummaryState
            OFFLINESTATE: Same as for SummaryState
            STANDBYSTATE: Same as for SummaryState
            MANUALREADINGSTATE: The electromere is currentnly storing data into the buffer
            and measurements are being published via the "intensity" event. This process
            will continue until a timeout happends (300seconds) or a stop command is executed
            DURATIONREADINGSTATE: The electromere is currentnly storing data into the buffer
            and measurements are being published via the "intensity" event. This process
            will continue until the time has passed or a stop command is executed
            CONFIGURINGSTATE: The electrometer goes to this detailedState while it changes any
            of the internal parameters to prevent conflicts sending multiple commands while
            the devices is being configured
            NOTREADINGSTATE: Not reading state and the device is ready to receive any command
            READINGBUFFERSTATE: The CSC is reading data from the electrometer buffer, this 
            could take a while and will use the communication protocol. This will prevent 
            the execution of any command
        """
        pass

    @abstractmethod
    def getState(self):
        """Returns the detailedState of the software
        """
        pass

    @abstractmethod
    def getMode(self):
        """Request the mode to the Electrometer then returns the value
        """
        pass

    @abstractmethod
    def getRange(self):
        """Request the configuration value of the range to the electrometer
        and returns it
        """
        pass

    @abstractmethod
    def getValue(self):
        """Request the last measurement made by the electrometer and returns
        it's value
        """
        pass

    @abstractmethod
    def getIntegrationTime(self):
        """Request the configuration value of the integration time to the 
        electrometer and returns it
        """
        pass

    @abstractmethod
    def setIntegrationTime(self, integrationTime, skipState=False):
        """Set the integration time to the electrometer and returns the value
        
        Arguments:
            integrationTime {float} -- Integration time value
            skipState {bool} -- Skip the state check done by the function (default: {False})
        """
        pass

    @abstractmethod
    def getErrorList(self):
        """Returns a list of error codes and messages obtained directly from the electrometer
        
        Returns:
            long<list>, string<list> -- error codes from the device, error messages from the device
        """
        pass

    @abstractmethod
    def setMode(self, mode, skipState=False):
        """Set the mode to read on the electrometer

        Arguments:
            mode {long} -- Mode used in the configuration file, 0-Current, 1-Charge, 2-Voltage, 
            3-Resistance

        Keyword Arguments:
            skipState {bool} -- Skip the state check done by the function (default: {False})
        """
        pass

    @abstractmethod
    def setRange(self, range, skipState=False):
        """Set measurement range, it will use the current unit selected

        Arguments:
            range {float} -- -1 for automatic range. Volts range from 0 t
            o 210 Volts, Current range from 0 to 21e-3 Amps, Resistance 
            from 0 to 100e18 Ohms, Charge from 0 to +2.1e-6 Coulombs

        Keyword Arguments:
            skipState {bool} -- Skip the state check done by the function (default: {False})
        """
        pass

    @abstractmethod
    def activateMedianFilter(self, activate, skipState=False):
        """The median filter is used to determine the “middle-most” reading from a 
        group of readings that are arranged according to size. Activate the median 
        filter inside the electrometer, 1 for ON and 0 for OFF

        Arguments:
            activate {bool} -- Activate or deactivate the filter

        Keyword Arguments:
            skipState {bool} -- Skip the state check done by the function (default: {False})
        """
        pass

    @abstractmethod
    def activateAverageFilter(self, activate, skipState=False):
        """Activate the average filter inside the electrometer, it uses the 
        Default value inside the device (last 10 readings) to do the average 
        calculation, 1 for ON and 0 for OFF

        Arguments:
            activate {bool} -- Activate or deactivate the filter

        Keyword Arguments:
            skipState {bool} -- Skip the state check done by the function (default: {False})
        """
        pass

    @abstractmethod
    def activateFilter(self, activate, skipState=False):
        """Activate the filter. If this is OFF (set to 0), none of the filters 
        will operate regardless of their settings below

        Arguments:
            activate {bool} -- Activate or deactivate the filter

        Keyword Arguments:
            skipState {bool} -- Skip the state check done by the function (default: {False})
        """
        pass

    @abstractmethod
    def getAverageFilterStatus(self):
        """Get the status of the average filter inside the electrometer

        Returns:
            bool -- Boolean that indicate if the filter is active
        """
        pass

    @abstractmethod
    def getMedianFilterStatus(self):
        """Get the status of the median filter inside the electrometer

        Returns:
            bool -- Boolean that indicate if the filter is active
        """
        pass

    @abstractmethod
    def getFilterStatus(self):
        """Get the status of the global filter inside the electrometer 
        If this is OFF (set to 0), none of the filters will operate regardless 
        of their settings below

        Returns:
            bool -- Boolean that indicate if the filter is active
        """
        pass

    @abstractmethod
    def configureCommunicator(self, port, baudrate, parity, stopbits, bytesize, byteToRead=1024, dsrdtr=False, xonxoff=False, timeout=2, termChar="\n"):
        """Publish settingsAppliedSerConf event to announce the 
        serial configuration event that it is used by the CSC

        Arguments:
            port {string} -- Visa resource or port
            baudrate {long} -- Baud rate as a number. allowed values are: 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200
            parity {long} -- Parity checking. PARITY_NONE=0, PARITY_EVEN=1, PARITY_ODD=2, PARITY_MARK=3, PARITY_SPACE=4
            stopbits {long} -- Number of stop bits. Possible values: 1, 2 
            bytesize {long} -- Number of stop bits. Possible values: 1, 2 

        Keyword Arguments:
            byteToRead {int} -- The maximum amount of bytes to read (default: {1024})
            dsrdtr {bool} -- hardware (DSR/DTR) flow control (default: {False})
            xonxoff {bool} -- Software flow control (default: {False})
            timeout {int} -- time out in seconds(default: {2})
            termChar {str} -- termination char, endl for end line(default: {"\n"})
        """
        pass

    @abstractmethod
    def restartBuffer(self):
        """Restart the buffer count inside the electrometer
        """
        pass

    @abstractmethod
    def getHardwareInfo(self):
        """Returns the electrometer information, including the ID


        Returns:
            string -- electrometer information, including the ID
        """
        pass

    @abstractmethod
    def getLastScanValues(self):
        """Get last measurement read from the device

        Returns:
            float -- Return the last value read, this could be old if no value
            has been read in a long time
        """
        pass

    def verifyValidState(self, validStates, skipVerification=False):
        """Verifies if current state is in validStates and raise an exception
        if not valid
        
        Arguments:
            validStates {Enum ElectrometerStates<list>} -- List of valid sates 
        
        Keyword Arguments:
            skipVerification {bool} -- Skip verification if true (default: {False})
        
        Raises:
            ValueError: Raise exeption if current state is not in validStates
        """
        if(skipVerification):
            return
        if(self.getState() not in validStates): raise ValueError(f"{currentframe().f_code.co_name} not allowed in {self.getState().name} state")


class ElectrometerStates(Enum):
    """detailedStates enumeration
    """
    DISABLEDSTATE = 1
    ENABLEDSTATE = 2
    FAULTSTATE = 3
    OFFLINESTATE = 4
    STANDBYSTATE = 5
    MANUALREADINGSTATE = 6
    DURATIONREADINGSTATE = 7
    CONFIGURINGSTATE = 8
    NOTREADINGSTATE = 9
    READINGBUFFERSTATE = 10


class ElectrometerErrors(Enum):
    NOERROR = 1
    ERROR = -1
    REJECTED = -2


class InitialEndValue(Enum):
    INITIAL = 0
    END = 1


class CommandValidStates():
    activateFilterValidStates = [ElectrometerStates.NOTREADINGSTATE]
    activateAverageFilterValidStates = [ElectrometerStates.NOTREADINGSTATE]
    activateMedianFilterValidStates = [ElectrometerStates.NOTREADINGSTATE]
    setRangeValidStates = [ElectrometerStates.NOTREADINGSTATE]
    setModeValidStates = [ElectrometerStates.NOTREADINGSTATE]
    readDuringTimeValidStates = [ElectrometerStates.NOTREADINGSTATE]
    performZeroCorrectionValidStates = [ElectrometerStates.NOTREADINGSTATE]
    readManualValidStates = [ElectrometerStates.NOTREADINGSTATE]
    setIntegrationTimeValidStates = [ElectrometerStates.NOTREADINGSTATE]
    stopReadingValidStates = [ElectrometerStates.MANUALREADINGSTATE]
    readBufferValidStates = [ElectrometerStates.MANUALREADINGSTATE,
                                  ElectrometerStates.DURATIONREADINGSTATE]

    def __init__(self):
        pass
