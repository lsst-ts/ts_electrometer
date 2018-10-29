from abc import ABC, abstractmethod
from enum import Enum


class IElectrometerController(ABC):

    def __init__(self):
        self.state = self.ElectrometerStates.OFFLINESTATE

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def isConnected(self):
        pass

    #Apply initial device configuration
    @abstractmethod
    def initialize(self, mode, range, integrationTime, medianFilterActive, avgFilterMode, avgFilterActive, filterActive):
        pass

    @abstractmethod
    def performZeroCorrection(self):
        pass

    @abstractmethod
    def readBuffer(self):
        pass

    @abstractmethod
    def startStoringToBuffer(self):
        pass

    @abstractmethod
    def readDuringTime(self, time):
        pass

    @abstractmethod
    def readManual(self):
        pass

    @abstractmethod
    def stopReading(self):
        pass

    @abstractmethod
    def stopStoringToBuffer(self):
        pass

    @abstractmethod
    def updateState(self, newState):
        pass

    @abstractmethod
    def getState(self):
        pass

    @abstractmethod
    def getMode(self):
        pass

    @abstractmethod
    def getRange(self):
        pass

    @abstractmethod
    def getValue(self):
        pass

    @abstractmethod
    def getIntegrationTime(self):
        pass

    @abstractmethod
    def setIntegrationTime(self, integrationTime):
        pass

    @abstractmethod
    def getErrorList(self):
        pass

    @abstractmethod
    def setMode(self, mode):
        pass

    @abstractmethod
    def setRange(self, range):
        pass

    @abstractmethod
    def activateMedianFilter(self, activate):
        pass

    @abstractmethod
    def activateAverageFilter(self, activate):
        pass

    @abstractmethod
    def activateFilter(self, activate):
        pass

    @abstractmethod
    def getAverageFilterStatus(self):
        pass

    @abstractmethod
    def getMedianFilterStatus(self):
        pass

    @abstractmethod
    def getFilterStatus(self):
        pass

    @abstractmethod
    def configureCommunicator(self, visaResource,baudRate,parity,dataBits,stopBits,flowControl,termChar):
        pass

    @abstractmethod
    def restartBuffer(self):
        pass

    @abstractmethod
    def getHardwareInfo(self):
        pass

    @abstractmethod
    def getLastScanValues(self):
        pass

    def verifyValidState(self, validStates, skipVerification=False):
        if(skipVerification):   return
        if(self.getState() not in validStates): raise ValueError(f"enable not allowed in {self.getState().name} state")

class ElectrometerStates(Enum):
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