import electrometerController.ElectrometerCommands as ec
from pythonCommunicator.SerialCommunicator import SerialCommunicator
from pythonFileReader.ConfigurationFileReaderYaml import FileReaderYaml
import electrometerController.IElectrometerController as iec
from time import time
from asyncio import sleep

class ElectrometerController(iec.IElectrometerController):

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
        self.readFreq = 0.01
        self.stopReadingValue = False
        self.configurationDelay = 0.1
        self.startAndEndScanValues = [[0,0], [0,0]] #[temperature, unit]
        self.autoRange = False


        self.serialPort = None
        self.state = iec.ElectrometerStates.STANDBYSTATE
        self.lastValue = 0
        self.stopReadingValue = False

    def connect(self):
        self.serialPort.connect()

    def disconnect(self):
        self.serialPort.disconnect()

    def isConnected(self):
        return self.serialPort.isConnected()

    def configureCommunicator(self, port, baudrate, parity, stopbits, bytesize, byteToRead=1024, dsrdtr=False, xonxoff=False, timeout=2, termChar="\n"):
        self.serialPort = SerialCommunicator(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, bytesize=bytesize, byteToRead=byteToRead, dsrdtr=dsrdtr, xonxoff=xonxoff, timeout=timeout, termChar=termChar)

    def getHardwareInfo(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getHardwareInfo())
        return self.serialPort.getMessage()

    def performZeroCorrection(self):
        self.verifyValidState(iec.CommandValidStates.performZeroCorrectionValidStates)
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE

        self.serialPort.sendMessage(ec.ElectrometerCommand.enableZeroCheck(True))
        self.serialPort.sendMessage(ec.ElectrometerCommand.setMode(self.mode))
        self.serialPort.sendMessage(ec.ElectrometerCommand.setRange(self.range))
        self.serialPort.sendMessage(ec.ElectrometerCommand.enableZeroCorrection(True))
        self.serialPort.sendMessage(ec.ElectrometerCommand.enableZeroCheck(False))

        self.state.value = iec.ElectrometerStates.NOTREADING

    async def readBuffer(self):
        self.verifyValidState(iec.CommandValidStates.readBufferValidStates)
        self.state = iec.ElectrometerStates.READINGBUFFER
        start = time()
        dt = 0
        self.restartBuffer()
        response = ""
        while(dt < 600): #Can't stay reading for longer thatn 10 minutes....
            await sleep(self.readFreq)
            self.serialPort.sendMessage(ec.ElectrometerCommand.readBuffer())
            response += self.serialPort.getMessage()
            dt = time() - start
            if(response.endswith(self.serialPort.termChar)): #Check if termination character is present
                break

        values, times = self.parseGetValues(response)
        self.state = iec.ElectrometerStates.NOTREADING
        return values, times

    def readManual(self):
        self.verifyValidState(iec.CommandValidStates.readManualValidStates)
        self.state = iec.ElectrometerStates.MANUALREADINGSTATE
        self.restartBuffer()
        self.stopReadingValue = False
        self.updateLastAndEndValue(iec.InitialEndValue.INITIAL)

    def updateLastAndEndValue(self, InitialEncIdex : iec.InitialEndValue):
        value, temperature, unit = self.getValue()
        self.startAndEndScanValues[InitialEncIdex.value] = [temperature, unit]

    async def stopReading(self):
        self.verifyValidState(iec.CommandValidStates.stopReadingValidStates)
        self.stopReadingValue = True
        self.stopStoringToBuffer()
        self.updateLastAndEndValue(iec.InitialEndValue.END)
        values, times = await self.readBuffer()
        return values, times

    def startStoringToBuffer(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.alwaysRead())

    def stopStoringToBuffer(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.stopReadingBuffer())

    async def readDuringTime(self, time):
        self.verifyValidState(iec.CommandValidStates.readDuringTimeValidStates)
        self.state = iec.ElectrometerStates.DURATIONREADINGSTATE
        start = time()
        dt = 0
        values = []
        self.restartBuffer()
        while(dt < time):
            sleep(self.readFreq)
            dt = time() - start
        self.stopStoringToBuffer()
        values, times = await self.readBuffer()
        self.state = iec.ElectrometerStates.NOTREADING
        return values, times

    def updateState(self, newState):
        self.state = newState

    def getState(self):
        return self.state

    def getMode(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getMode())
        modeStr = self.serialPort.getMessage()
        if(str(modeStr).__contains__("VOLT")):
            mode = ec.UnitMode.VOLT
        if(str(modeStr).__contains__("CURR")):
            mode = ec.UnitMode.CURR
        if(str(modeStr).__contains__("CHAR")):
            mode = ec.UnitMode.CHAR
        else:
            mode = ec.UnitMode.RES
        self.mode = mode
        return mode

    def getRange(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getRange(self.mode))
        self.range = float(self.serialPort.getMessage())
        return self.range

    def getValue(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getMeasure(ec.readingOption.LATEST))
        response = self.serialPort.getMessage()
        self.lastValue, temperature, unit = self.parseGetValues(response)
        return self.lastValue, temperature, unit

    def getIntegrationTime(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getIntegrationTime(self.mode))
        self.integrationTime = float(self.serialPort.getMessage())
        return self.integrationTime

    def setIntegrationTime(self, integrationTime, skipState=False):
        self.verifyValidState(iec.CommandValidStates.setIntegrationTimeValidStates, skipState)
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE
        self.serialPort.sendMessage(ec.ElectrometerCommand.integrationTime(self.mode, integrationTime))
        self.state.value = iec.ElectrometerStates.NOTREADING
        self.integrationTime = integrationTime

    def getErrorList(self):
        completeResponse = ""
        for i in range(100): #Maximum of 100
            self.serialPort.sendMessage(ec.ElectrometerCommand.getIntegrationTime(self.mode))
            reponse = self.serialPort.getMessage()
            if(len(reponse)==0): #break if there are no more errors in the queue (empty response)
                break
            completeResponse += reponse
        errorCodes, errorMessages = self.parseErrorString(response)
        return

    def setMode(self, mode, skipState=False):
        self.verifyValidState(iec.CommandValidStates.setModeValidStates, skipState)
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE
        self.serialPort.sendMessage(ec.ElectrometerCommand.setMode(self.mode))
        self.state.value = iec.ElectrometerStates.NOTREADING
        self.mode = mode
        return self.mode

    def setRange(self, range, skipState=False):
        self.verifyValidState(iec.CommandValidStates.setRangeValidStates, skipState)
        auto = True if range<0 else False
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE
        self.serialPort.sendMessage(ec.ElectrometerCommand.setRange(auto, range, self.mode))
        self.state.value = iec.ElectrometerStates.NOTREADING
        self.range = range
        self.autoRange = auto
        return self.range

    def activateMedianFilter(self, activate, skipState=False):
        self.verifyValidState(iec.CommandValidStates.activateMedianFilterValidStates, skipState)
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE
        self.serialPort.sendMessage(ec.ElectrometerCommand.activateFilter(self.mode, ec.Filter.MED, activate))
        self.state.value = iec.ElectrometerStates.NOTREADING
        self.medianFilterActive = activate
        return activate

    def activateAverageFilter(self, activate, skipState=False):
        self.verifyValidState(iec.CommandValidStates.activateAverageFilterValidStates, skipState)
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE
        self.serialPort.sendMessage(ec.ElectrometerCommand.activateFilter(self.mode, ec.Filter.AVER, activate))
        self.state.value = iec.ElectrometerStates.NOTREADING
        self.avgFilterActive = activate
        return activate

    def activateFilter(self, activate, skipState=False):
        self.verifyValidState(iec.CommandValidStates.activateFilterValidStates, skipState)
        self.activateMedianFilter(activate)
        self.activateAverageFilter(activate)
        self.filterActive = activate
        return activate

    def getAverageFilterStatus(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getAvgFilterStatus(self.mode))
        self.avgFilterActive = True if self.serialPort.getMessage().__contains__("ON") else False
        return self.avgFilterActive

    def getMedianFilterStatus(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getMedFilterStatus(self.mode))
        self.medianFilterActive = True if self.serialPort.getMessage().__contains__("ON") else False
        return self.medianFilterActive

    def restartBuffer(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.clearBuffer())
        self.serialPort.sendMessage(ec.ElectrometerCommand.setBufferSize())
        self.serialPort.sendMessage(ec.ElectrometerCommand.alwaysRead())

    def getLastScanValues(self):
        #Returns values stored at the beggining of the manual and time scan
        return self.startAndEndScanValues

    def parseErrorString(self, errorMessage):
        print("Create parseErrorString parser!!!")
        return [0], "Reading available"

    def parseGetValues(self, response):
        print("Create parseGetValues parser!!!")
        intensity, temperature, unit = 0, 0, 0, "A"
        return intensity, time, temperature, unit

if __name__ == "__main__":
    electrometer = ElectrometerController()
    electrometer.configureCommunicator(port="/dev/electrometer", baudrate=57600, parity=1, stopbits=1, bytesize=8, byteToRead=128, dsrdtr=0, xonxoff=0, timeout=1, termChar="\r")
