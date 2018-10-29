import electrometerController.IElectrometerController as iec
from electrometerController.ElectrometerCommands import UnitMode, AverFilterType
from random import randint
from asyncio import sleep
import time

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
        self.startAndEndScanValues = [[0,0], [0,0]] #[temperature, unit]

    def connect(self):
        self.connected = True
        return

    def disconnect(self):
        self.connected = False
        return 

    def isConnected(self):
        return self.connected

    def configureCommunicator(self, port, baudrate, parity, stopbits, bytesize, byteToRead=1024, dsrdtr=False, xonxoff=False, timeout=2, termChar="\n"):
        self.connect()
        return

    def getHardwareInfo(self):
        return "Simulation"

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
        self.updateLastAndEndValue(iec.InitialEndValue.INITIAL)
        self.state = iec.ElectrometerStates.MANUALREADINGSTATE

    def updateLastAndEndValue(self, InitialEncIdex : iec.InitialEndValue):
        value, temperature, unit = self.getValue()
        self.startAndEndScanValues[InitialEncIdex.value] = [temperature, unit]

    async def stopReading(self):
        self.verifyValidState(iec.CommandValidStates.stopReadingValidStates)
        print("Command stopReading executed...")
        self.stopReadingValue = True
        self.updateLastAndEndValue(iec.InitialEndValue.END)
        values, times = await self.readBuffer()
        return values, times


    def startStoringToBuffer(self):
        print("Command startStoringToBuffer executed...")
        return 

    def stopStoringToBuffer(self):
        print("Command stopStoringToBuffer executed...")
        return

    async def readDuringTime(self, readTime):
        self.verifyValidState(iec.CommandValidStates.readDuringTimeValidStates)
        self.state = iec.ElectrometerStates.DURATIONREADINGSTATE
        self.updateLastAndEndValue(iec.InitialEndValue.INITIAL)
        start = time.time()
        values = []
        dt = 0
        while (dt < readTime):
            await sleep(self.readFreq)
            dt = time.time() - start
        self.updateLastAndEndValue(iec.InitialEndValue.END)
        values, times = await self.readBuffer()
        print("Command readDuringTime executed...")
        self.state = iec.ElectrometerStates.NOTREADINGSTATE
        return values, times

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
        temperature = 20.0+ randint(0,100)/100.0
        return self.lastValue, temperature, unit

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
        return [0], ["Reading available"]

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

    def getLastScanValues(self):
        #Returns values stored at the beggining of the manual and time scan
        return self.startAndEndScanValues

if __name__ == "__main__":
    print("Test")
