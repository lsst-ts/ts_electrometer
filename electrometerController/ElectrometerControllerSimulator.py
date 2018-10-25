import IElectrometerController as iec
from ElectrometerCommands import UnitMode, AverFilterType
from random import randint
from asyncio import sleep
from datetime import datetime

class ElectrometerSimulator(iec.IElectrometerController):

    def __init__(self):
        self.mode = UnitMode.CURR
        self.range = 0.1
        self.integrationTime = 0.01
        self.state = iec.ElectrometerStates.STANDBYSTATE
        self.medianFilterActive = False
        self.avgFilterMode = AverFilterType.NONE
        self.avgFilterActive = False
        self.connected = False
        self.SerialConfiguration = FileReaderYaml("..\\settingFiles", "Test", 1) #Needs to be updated at start
        self.SerialConfiguration.loadFile("serialConfiguration")
        self.stopReading = False
        self.lastValue = 0
        self.readFreq = 0.1

    def connect(self):
        self.connected = True
        return iec.ElectrometerErrors.NOERROR.value

    def disconnect(self):
        self.connected = False
        return iec.ElectrometerErrors.NOERROR.value

    def isConnected(self):
        return self.connected

    def configureCommunicator(self):
        return iec.ElectrometerErrors.NOERROR.value

    def initialize(self, mode, range, integrationTime, medianFilterActive, avgFilterMode, avgFilterActive):
        self.mode = mode
        self.range = range
        self.integrationTime = integrationTime
        self.medianFilterActive = medianFilterActive
        self.avgFilterMode = avgFilterMode
        self.avgFilterActive = avgFilterActive
        return iec.ElectrometerErrors.NOERROR.value

    def performZeroCorrection(self):
        return iec.ElectrometerErrors.NOERROR.value

    def readBuffer(self):
        if(self.state != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED, []
        self.stopReading = False
        self.state != iec.ElectrometerStates.READINGBUFFER
        values = []
        iterations = 1000
        for i in range(iterations):
            self.lastValue = self.getValue()
            values.append(self.lastValue)
            sleep(self.integrationTime)
        self.state != iec.ElectrometerStates.NOTREADING
        self.stopReading = False
        return iec.ElectrometerErrors.NOERROR.value, values


    def readManual(self, maxtime):
        if (self.state != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED, []
        self.stopReading = False
        self.state != iec.ElectrometerStates.MANUALREADINGSTATE
        start = datetime.now()
        values = []
        dt = 0
        while (dt < maxtime):
            sleep(self.readFreq)
            values.append(self.getValue())
            if(self.stopReading):
                break
            dt = datetime.now() - start
        self.state = iec.ElectrometerStates.NOTREADING
        return iec.ElectrometerErrors.NOERROR, values

    def stopReading(self):
        self.stopReading = True


    def startStoringToBuffer(self):
        return iec.ElectrometerErrors.NOERROR.value

    def readDuringTime(self, time):
        if (self.state != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED, []
        self.state = iec.ElectrometerStates.DURATIONREADINGSTATE
        start = datetime.now()
        values = []
        dt = 0
        while (dt < time):
            sleep(self.readFreq)
            values.append(self.getValue())
            if(self.stopReading):
                break
            dt = datetime.now() - start
        self.state = iec.ElectrometerStates.NOTREADING
        return iec.ElectrometerErrors.NOERROR, values

    def stopStoringToBuffer(self):
        return iec.ElectrometerErrors.NOERROR.value

    def updateState(self, newState):
        self.state = newState
        return iec.ElectrometerErrors.NOERROR.value

    def getState(self):
        return self.state

    def getMode(self):
        return self.mode

    def getRange(self):
        return self.range

    def getValue(self):
        return randint(1, 100)*self.range/1000.0

    def getIntegrationTime(self):
        return self.integrationTime

    def setIntegrationTime(self, integrationTime):
        self.integrationTime = integrationTime
        return iec.ElectrometerErrors.NOERROR.value

    def getErrorList(self):
        return [0]

    def setMode(self, mode):
        self.mode = mode
        return iec.ElectrometerErrors.NOERROR.value

    def setRange(self, range):
        self.range = range
        return iec.ElectrometerErrors.NOERROR.value

    def activateMedianFilter(self, activate):
        self.medianFilterActive = activate
        return iec.ElectrometerErrors.NOERROR.value

    def activateAverageFilter(self, activate):
        self.avgFilterActive = activate
        return iec.ElectrometerErrors.NOERROR.value

    def getAverageFilterStatus(self):
        return self.avgFilterMode, self.avgFilterActive

    def getMedianFilterStatus(self):
        return self.medianFilterActive

    def updateSerialConfiguration(self, path, settingsSet, settingsVersion):
        self.SerialConfiguration = FileReaderYaml(path, settingsSet, settingsVersion)
        self.SerialConfiguration.loadFile("serialConfiguration")
        return iec.ElectrometerErrors.NOERROR.value

    def restartBuffer(self):
        return iec.ElectrometerErrors.NOERROR.value


if __name__ == "__main__":
    print("Test")