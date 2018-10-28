import electrometerController.IElectrometerController as iec
from electrometerController.ElectrometerCommands import UnitMode, AverFilterType
from random import randint
from asyncio import sleep
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
        self.lastValue = 0
        self.readFreq = 0.1
        self.stopReadingValue = False
        self.configurationDelay = 0.1

    def connect(self):
        self.connected = True
        return

    def disconnect(self):
        self.connected = False
        return 

    def isConnected(self):
        return self.connected

    def configureCommunicator(self, visaResource,baudRate,parity,dataBits,stopBits,flowControl,termChar):
        self.connect()
        return

    def initialize(self, mode, range, integrationTime, medianFilterActive, avgFilterMode, avgFilterActive):
        self.mode = mode
        self.range = range
        self.integrationTime = integrationTime
        self.medianFilterActive = medianFilterActive
        self.avgFilterMode = avgFilterMode
        self.avgFilterActive = avgFilterActive
        print("Initialize executed...")
        return

    def performZeroCorrection(self):
        print("Command performZeroCorrection executed...")
        return

    async def readBuffer(self):
        self.verifyValidState(iec.CommandValidStates.readBufferValidStates)
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
            await sleep(self.integrationTime)
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        self.stopReadingValue = False
        print("Command readBuffer executed...")
        return values, times


    def readManual(self):
        self.verifyValidState(iec.CommandValidStates.readManualValidStates)
        self.stopReadingValue = False
        self.state = iec.ElectrometerStates.MANUALREADINGSTATE
        return 

    async def stopReading(self):
        self.verifyValidState(iec.CommandValidStates.stopReadingValidStates)
        print("Command stopReading executed...")
        self.stopReadingValue = True
        values, times = await self.readBuffer()
        return values, times


    def startStoringToBuffer(self):
        print("Command startStoringToBuffer executed...")
        return 

    async def readDuringTime(self, readTime):
        self.verifyValidState(iec.CommandValidStates.readDuringTimeValidStates)
        self.state = iec.ElectrometerStates.DURATIONREADINGSTATE
        start = time.time()
        values = []
        dt = 0
        while (dt < readTime):
            await sleep(self.readFreq)
            dt = time.time() - start
        values, times = await self.readBuffer()
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

    def setIntegrationTime(self, integrationTime, skipState=False):
        self.verifyValidState(iec.CommandValidStates.setIntegrationTimeValidStates, skipState)
        self.state = iec.ElectrometerStates.CONFIGURINGSTATE
        self.integrationTime = integrationTime
        sleep(self.configurationDelay)
        print("Command setIntegrationTime executed...")
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        return self.integrationTime

    def getErrorList(self):
        return [0]

    def setMode(self, mode, skipState=False):
        self.verifyValidState(iec.CommandValidStates.setModeValidStates, skipState)
        self.state = iec.ElectrometerStates.CONFIGURINGSTATE
        self.mode = mode
        sleep(self.configurationDelay)
        print("Command setMode executed...")
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        return self.mode

    def setRange(self, range, skipState=False):
        self.verifyValidState(iec.CommandValidStates.setRangeValidStates, skipState)
        self.state = iec.ElectrometerStates.CONFIGURINGSTATE
        self.range = range
        sleep(self.configurationDelay)
        print("Command setRange executed...")
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        return self.range

    def activateMedianFilter(self, activate, skipState=False):
        self.verifyValidState(iec.CommandValidStates.activateMedianFilterValidStates, skipState)
        self.state = iec.ElectrometerStates.CONFIGURINGSTATE
        self.medianFilterActive = activate
        sleep(self.configurationDelay)
        print("Command activateMedianFilter executed...")
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        return self.medianFilterActive

    def activateAverageFilter(self, activate, skipState=False):
        self.verifyValidState(iec.CommandValidStates.activateAverageFilterValidStates, skipState)
        self.state = iec.ElectrometerStates.CONFIGURINGSTATE
        self.avgFilterActive = activate
        sleep(self.configurationDelay)
        print("Command activateAverageFilter executed...")
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        return self.avgFilterActive

    def activateFilter(self, activate, skipState=False):
        self.verifyValidState(iec.CommandValidStates.activateFilterValidStates, skipState)

        self.state = iec.ElectrometerStates.CONFIGURINGSTATE
        self.filterActive = activate
        self.state = iec.ElectrometerStates.NOTREADINGSTATE

        self.activateMedianFilter(activate)
        self.activateAverageFilter(activate)

        sleep(self.configurationDelay)
        print("Command activateFilter executed...")
        return self.filterActive

    def getAverageFilterStatus(self):
        return self.avgFilterActive

    def getMedianFilterStatus(self):
        return self.medianFilterActive

    def getFilterStatus(self):
        return self.filterActive

    def restartBuffer(self):
        print("Command restartBuffer executed...")
        return 


if __name__ == "__main__":
    print("Test")
