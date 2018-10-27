from abc import ABC, abstractmethod
from enum import Enum


class IElectrometerController(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def isConnected(self):
        pass

    @abstractmethod
    def configureCommunicator(self):
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
    def updateSerialConfiguration(self, settingsSet, settingsVersion):
        pass

    @abstractmethod
    def restartBuffer(self):
        pass

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
