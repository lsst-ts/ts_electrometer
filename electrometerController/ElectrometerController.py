import electrometerController.ElectrometerCommands as ec
from pythonCommunicator.SerialCommunicator import SerialCommunicator
from pythonFileReader.ConfigurationFileReaderYaml import FileReaderYaml
import electrometerController.IElectrometerController as iec
from datetime import datetime
from asyncio import sleep

class ElectrometerController(iec.IElectrometerController):

    def __init__(self):

        self.mode = ec.UnitMode.CURR
        self.range = 0.1
        self.integrationTime = 0.001
        self.state = iec.ElectrometerStates.STANDBYSTATE
        self.medianFilterActive = False
        self.avgFilterMode = ec.AverFilterType.NONE
        self.avgFilterActive = False
        self.autoRange = False

        self.readFreq = 0.1

        self.commands = ec.ElectrometerCommand()
        self.serialPort = None
        self.SerialConfiguration = FileReaderYaml("settingFiles", "Test", 1) #Needs to be updated at start
        #self.SerialConfiguration.loadFile("serialConfiguration")
        self.state = iec.ElectrometerStates.STANDBYSTATE
        self.lastValue = 0
        self.stopReadingValue = False

    def configureCommunicator(self):
        baudrate = self.SerialConfiguration.readValue('baudrate')
        port = self.SerialConfiguration.readValue('port')
        parity = self.SerialConfiguration.readValue('parity')
        stopBits = self.SerialConfiguration.readValue('stopBits')
        byteSize = self.SerialConfiguration.readValue('byteSize')
        byteToRead = self.SerialConfiguration.readValue('byteToRead')
        timeout = self.SerialConfiguration.readValue('timeout')
        xonxoff = self.SerialConfiguration.readValue('xonxoff')
        dsrdtr = self.SerialConfiguration.readValue('dsrdtr')
        termChar = self.SerialConfiguration.readValue('termChar')
        self.serialPort = SerialCommunicator(port=port, baudrate=baudrate, parity=parity, stopbits=stopBits, bytesize=byteSize, byteToRead=byteToRead, dsrdtr=dsrdtr, xonxoff=xonxoff, timeout=timeout, termChar=termChar)

    def connect(self):
        ERROR, e = self.serialPort.connect()
        return ERROR, e

    def disconnect(self):
        self.serialPort.disconnect()

    def isConnected(self):
        return self.serialPort.isConnected()

    def initialize(self, mode, range, integrationTime, medianFilterActive, avgFilterMode, avgFilterActive):

        if(self.state.value != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED

        #Update state to configuring
        self.updateState(iec.ElectrometerStates.CONFIGURINGSTATE)

        self.setMode(mode)
        self.setRange(range)
        self.setIntegrationTime(integrationTime)
        self.activateAverageFilter(avgFilterMode, avgFilterActive)
        self.activateMedianFilter(medianFilterActive)

        #Update state to not reading and ready for next command
        self.updateState(iec.ElectrometerStates.NOTREADING)
        self.mode = mode
        self.range = range
        self.integrationTime = integrationTime
        self.avgFilterActive = avgFilterActive
        return iec.ElectrometerErrors.NOERROR

    def stopReading(self):
        self.stopReadingValue = True

    def performZeroCorrection(self):
        if (self.state.value != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE

        self.serialPort.sendMessage(ec.ElectrometerCommand.enableZeroCheck(True))
        self.serialPort.sendMessage(ec.ElectrometerCommand.setMode(self.mode))
        self.serialPort.sendMessage(ec.ElectrometerCommand.setRange(self.range))
        self.serialPort.sendMessage(ec.ElectrometerCommand.enableZeroCorrection(True))
        self.serialPort.sendMessage(ec.ElectrometerCommand.enableZeroCheck(False))

        self.state.value = iec.ElectrometerStates.NOTREADING
        return iec.ElectrometerErrors.NOERROR

    def startStoringToBuffer(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.alwaysRead())
        return iec.ElectrometerErrors.NOERROR

    def stopStoringToBuffer(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.stopReadingBuffer())
        return iec.ElectrometerErrors.NOERROR

    def updateState(self, newState):
        self.state = newState

    def readDuringTime(self, time):
        if (self.state != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED, []
        self.state = iec.ElectrometerStates.DURATIONREADINGSTATE
        start = datetime.now()
        dt = 0
        values = []
        self.restartBuffer()
        while(dt < time):
            sleep(self.readFreq)
            self.serialPort.sendMessage(ec.ElectrometerCommand.getMeasure(ec.readingOption.LATEST))
            response = self.serialPort.getMessage()
            intensity, temperature, unit = self.parseGetValues(response)
            self.lastValue = intensity
            if(self.stopReadingValue):
                break
            dt = datetime.now() - start

        self.stopReadingValue = False
        self.state = iec.ElectrometerStates.NOTREADING
        return iec.ElectrometerErrors.NOERROR, values

    def getState(self):
        return self.state

    def getValue(self):
        return self.lastValue

    def readBuffer(self):
        if (self.state != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED, []
        self.state != iec.ElectrometerStates.READINGBUFFER
        start = datetime.now()
        dt = 0
        values = []
        self.restartBuffer()
        while(dt < 600): #Can't stay reading for longer thatn 10 minutes....
            sleep(self.readFreq)
            self.serialPort.sendMessage(ec.ElectrometerCommand.readBuffer())
            response = self.serialPort.getMessage()
            intensity, temperature, unit = self.parseGetValues(response)
            self.lastValue = intensity
            if(self.stopReadingValue):
                break
            dt = datetime.now() - start

        self.stopReadingValue = False
        self.state = iec.ElectrometerStates.NOTREADING
        return iec.ElectrometerErrors.NOERROR, values

    def readManual(self):
        if (self.state != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED, []
        self.state != iec.ElectrometerStates.MANUALREADINGSTATE
        start = datetime.now()
        dt = 0
        values = []
        self.restartBuffer()
        while(dt < maxtime):
            sleep(self.readFreq)
            self.serialPort.sendMessage(ec.ElectrometerCommand.getMeasure(ec.readingOption.LATEST))
            response = self.serialPort.getMessage()
            intensity, temperature, unit = self.parseGetValues(response)
            self.lastValue = intensity
            if(self.stopReadingValue):
                break
            dt = datetime.now() - start

        self.stopReadingValue = False
        self.state = iec.ElectrometerStates.NOTREADING
        return iec.ElectrometerErrors.NOERROR, values

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
        return iec.ElectrometerErrors.NOERROR, mode

    def getRange(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getRange(self.mode))
        self.range = float(self.serialPort.getMessage())
        return self.range

    def getIntegrationTime(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getIntegrationTime(self.mode))
        self.integrationTime = float(self.serialPort.getMessage())
        return self.range

    def getErrorList(self):
        pass

    def getAverageFilterStatus(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getAvgFilterStatus(self.mode))
        self.avgFilterActive = True if self.serialPort.getMessage().__contains__("ON") else False
        return self.avgFilterActive

    def getMedianFilterStatus(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.getMedFilterStatus(self.mode))
        self.medianFilterActive = True if self.serialPort.getMessage().__contains__("ON") else False
        return self.medianFilterActive


    def parseGetValues(self, response):
        print("Create parser!!!")
        intensity, temperature, unit = 0, 0, "A"
        return 0, 0, 0

    def setMode(self, mode):
        if (self.state.value != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE

        self.serialPort.sendMessage(ec.ElectrometerCommand.setMode(self.mode))

        self.state.value = iec.ElectrometerStates.NOTREADING
        self.mode = mode
        return iec.ElectrometerErrors.NOERROR

    def setRange(self, auto, range):
        if (self.state.value != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE

        self.serialPort.sendMessage(ec.ElectrometerCommand.setRange(auto, range, self.mode))

        self.state.value = iec.ElectrometerStates.NOTREADING
        self.range = range
        self.autoRange = auto

        return iec.ElectrometerErrors.NOERROR

    def activateMedianFilter(self, activate):
        if (self.state.value != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE

        self.serialPort.sendMessage(ec.ElectrometerCommand.activateFilter(self.mode, ec.Filter.MED, activate))

        self.state.value = iec.ElectrometerStates.NOTREADING
        self.medianFilterActive = activate
        return iec.ElectrometerErrors.NOERROR

    def activateAverageFilter(self, activate):
        if (self.state.value != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE

        self.serialPort.sendMessage(ec.ElectrometerCommand.activateFilter(self.mode, ec.Filter.AVER, activate))

        self.state.value = iec.ElectrometerStates.NOTREADING
        self.avgFilterActive = activate
        return iec.ElectrometerErrors.NOERROR

    def updateSerialConfiguration(self, path, settingsSet, settingsVersion):
        self.SerialConfiguration = FileReaderYaml(path, settingsSet, settingsVersion)
        self.SerialConfiguration.loadFile("serialConfiguration")
        return iec.ElectrometerErrors.NOERROR.value

    def restartBuffer(self):
        self.serialPort.sendMessage(ec.ElectrometerCommand.clearBuffer())
        self.serialPort.sendMessage(ec.ElectrometerCommand.setBufferSize())
        self.serialPort.sendMessage(ec.ElectrometerCommand.alwaysRead())
        return iec.ElectrometerErrors.NOERROR.value

    def setIntegrationTime(self, integrationTime):
        if (self.state.value != iec.ElectrometerStates.NOTREADING): return iec.ElectrometerErrors.REJECTED
        self.state.value = iec.ElectrometerStates.CONFIGURINGSTATE

        self.serialPort.sendMessage(ec.ElectrometerCommand.integrationTime(self.mode, integrationTime))

        self.state.value = iec.ElectrometerStates.NOTREADING
        self.integrationTime = integrationTime
        return iec.ElectrometerErrors.NOERROR
