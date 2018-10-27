import electrometerController.IElectrometerController as iec
from electrometerController.ElectrometerCommands import UnitMode, AverFilterType
from random import randint
from asyncio import sleep
from datetime import datetime
import time
from pythonFileReader.ConfigurationFileReaderYaml import FileReaderYaml

class ElectrometerSimulator(iec.IElectrometerController):

    def __init__(self):
        self.mode = UnitMode.CURR
        self.range = 0.1
        self.integrationTime = 0.01
        self.state = iec.ElectrometerStates.STANDBYSTATE
        self.medianFilterActive = False
        self.filterActive = False
        self.avgFilterMode = AverFilterType.NONE
        self.avgFilterActive = False
        self.connected = False
        self.SerialConfiguration = FileReaderYaml("../settingFiles", "Test", 1) #Needs to be updated at start
        self.SerialConfiguration.loadFile("serialConfiguration")
        self.lastValue = 0
        self.readFreq = 0.1
        self.stopReadingValue = False

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
        print("Initialize executed...")
        return iec.ElectrometerErrors.NOERROR.value

    def performZeroCorrection(self):
        print("Command performZeroCorrection executed...")
        return iec.ElectrometerErrors.NOERROR.value

    def readBuffer(self):
        if(self.state != iec.ElectrometerStates.DURATIONREADINGSTATE and self.state != iec.ElectrometerStates.MANUALREADINGSTATE): raise ValueError(f"enable not allowed in {self.getState().name} state")
        self.stopReadingValue = False
        self.state = iec.ElectrometerStates.READINGBUFFERSTATE
        values = []
        times = []
        initialTime = time.time()
        iterations = 1000
        for i in range(iterations):
            self.lastValue = self.getValue()[0]
            values.append(self.lastValue)
            dt = time.time() - initialTime
            times.append(dt)
            sleep(self.integrationTime)
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        self.stopReadingValue = False
        print("Command readBuffer executed...")
        return values, times


    def readManual(self):
        if (self.state != iec.ElectrometerStates.NOTREADINGSTATE): raise ValueError(f"enable not allowed in {self.getState().name} state")
        self.stopReadingValue = False
        self.state = iec.ElectrometerStates.MANUALREADINGSTATE
        return 

    def stopReading(self):
        print("Command stopReading executed...")
        self.stopReadingValue = True
        values, times = self.readBuffer()
        return values, times


    def startStoringToBuffer(self):
        print("Command startStoringToBuffer executed...")
        return 

    def readDuringTime(self, time):
        if (self.state != iec.ElectrometerStates.NOTREADINGSTATE): raise ValueError(f"enable not allowed in {self.getState().name} state")
        self.state = iec.ElectrometerStates.DURATIONREADINGSTATE
        start = datetime.now()
        values = []
        dt = 0
        while (dt < time):
            sleep(self.readFreq)
            values.append(self.getValue()[0])
            if(self.stopReadingValue):
                break
            dt = datetime.now() - start
        values, times = self.readBuffer()
        print("Command readDuringTime executed...")
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        return values, times

    def stopStoringToBuffer(self):
        print("Command stopStoringToBuffer executed...")
        return 

    def updateState(self, newState):
        self.state = newState
        return

    def getState(self):
        return self.state

    def getMode(self):
        return self.mode

    def getRange(self):
        return self.range

    def getValue(self):
        self.lastValue = randint(1, 100)*self.range/1000.0
        unit = "A" if self.mode == UnitMode.CURR else "C"
        return self.lastValue, unit

    def getIntegrationTime(self):
        return self.integrationTime

    def setIntegrationTime(self, integrationTime):
        self.integrationTime = integrationTime
        print("Command setIntegrationTime executed...")
        return self.integrationTime

    def getErrorList(self):
        return [0]

    def setMode(self, mode):
        self.mode = mode
        print("Command setMode executed...")
        return self.mode

    def setRange(self, range):
        self.range = range
        print("Command setRange executed...")
        return self.range

    def activateMedianFilter(self, activate):
        self.medianFilterActive = activate
        print("Command activateMedianFilter executed...")
        return iec.ElectrometerErrors.NOERROR.value, self.medianFilterActive

    def activateAverageFilter(self, activate):
        self.avgFilterActive = activate
        print("Command activateAverageFilter executed...")
        return self.avgFilterActive

    def activateFilter(self, activate):
        self.filterActive = activate
        print("Command activateFilter executed...")
        return self.avgFilterActive

    def getAverageFilterStatus(self):
        return self.avgFilterMode, self.avgFilterActive

    def getMedianFilterStatus(self):
        return self.medianFilterActive

    def getFilterStatus(self):
        return self.filterActive

    def updateSerialConfiguration(self, path, settingsSet, settingsVersion):
        self.SerialConfiguration = FileReaderYaml(path, settingsSet, settingsVersion)
        self.SerialConfiguration.loadFile("serialConfiguration")
        print("Updated Serial Configuration:\npath: "+path+"\nsettingsSet: "+settingsSet+"\nsettingsVersion:"+settingsVersion)
        return iec.ElectrometerErrors.NOERROR.value

    def restartBuffer(self):
        print("Command restartBuffer executed...")
        return iec.ElectrometerErrors.NOERROR.value


if __name__ == "__main__":
    print("Test")
