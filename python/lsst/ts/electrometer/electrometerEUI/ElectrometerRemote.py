import time
from SALPY_Electrometer import *

class ElectrometerRemote:
    def __init__(self):
        self.sal = SAL_Electrometer(1)
        self.sal.setDebugLevel(0)
        self.sal.salCommand("Electrometer_command_abort")
        self.sal.salCommand("Electrometer_command_enable")
        self.sal.salCommand("Electrometer_command_disable")
        self.sal.salCommand("Electrometer_command_standby")
        self.sal.salCommand("Electrometer_command_exitControl")
        self.sal.salCommand("Electrometer_command_start")
        self.sal.salCommand("Electrometer_command_enterControl")
        self.sal.salCommand("Electrometer_command_setValue")
        self.sal.salCommand("Electrometer_command_performZeroCalib")
        self.sal.salCommand("Electrometer_command_setDigitalFilter")
        self.sal.salCommand("Electrometer_command_setIntegrationTime")
        self.sal.salCommand("Electrometer_command_setMode")
        self.sal.salCommand("Electrometer_command_setRange")
        self.sal.salCommand("Electrometer_command_startScan")
        self.sal.salCommand("Electrometer_command_startScanDt")
        self.sal.salCommand("Electrometer_command_stopScan")

        self.sal.salEvent("Electrometer_logevent_settingVersions")
        self.sal.salEvent("Electrometer_logevent_errorCode")
        self.sal.salEvent("Electrometer_logevent_summaryState")
        self.sal.salEvent("Electrometer_logevent_appliedSettingsMatchStart")
        self.sal.salEvent("Electrometer_logevent_detailedState")
        self.sal.salEvent("Electrometer_logevent_digitalFilterChange")
        self.sal.salEvent("Electrometer_logevent_heartbeat")
        self.sal.salEvent("Electrometer_logevent_integrationTime")
        self.sal.salEvent("Electrometer_logevent_intensity")
        self.sal.salEvent("Electrometer_logevent_largeFileObjectAvailable")
        self.sal.salEvent("Electrometer_logevent_measureRange")
        self.sal.salEvent("Electrometer_logevent_measureType")
        self.sal.salEvent("Electrometer_logevent_settingsAppliedReadSets")
        self.sal.salEvent("Electrometer_logevent_settingsAppliedSerConf")
        self.sal.salEvent("Electrometer_logevent_deviceErrorCode")


        self.eventSubscribers_settingVersions = []
        self.eventSubscribers_errorCode = []
        self.eventSubscribers_summaryState = []
        self.eventSubscribers_appliedSettingsMatchStart = []
        self.eventSubscribers_detailedState = []
        self.eventSubscribers_digitalFilterChange = []
        self.eventSubscribers_heartbeat = []
        self.eventSubscribers_integrationTime = []
        self.eventSubscribers_intensity = []
        self.eventSubscribers_largeFileObjectAvailable = []
        self.eventSubscribers_measureRange = []
        self.eventSubscribers_measureType = []
        self.eventSubscribers_settingsAppliedReadSets = []
        self.eventSubscribers_settingsAppliedSerConf = []
        self.eventSubscribers_deviceErrorCode = []


        self.topicsSubscribedToo = {}

    def close(self):
        time.sleep(1)
        self.sal.salShutdown()

    def flush(self, action):
        result, data = action()
        while result >= 0:
            result, data = action()
            
    def checkForSubscriber(self, action, subscribers):
        buffer = []
        result, data = action()
        while result == 0:
            buffer.append(data)
            result, data = action()
        if len(buffer) > 0:
            for subscriber in subscribers:
                subscriber(buffer)
            
    def runSubscriberChecks(self):
        for subscribedTopic in self.topicsSubscribedToo:
            action = self.topicsSubscribedToo[subscribedTopic][0]
            subscribers = self.topicsSubscribedToo[subscribedTopic][1]
            self.checkForSubscriber(action, subscribers)
            
    def getEvent(self, action):
        lastResult, lastData = action()
        while lastResult >= 0:
            result, data = action()
            if result >= 0:
                lastResult = result
                lastData = data
            elif result < 0:
                break
        return lastResult, lastData


    def issueCommand_abort(self, value):
        data = Electrometer_command_abortC()
        data.value = value

        return self.sal.issueCommand_abort(data)

    def getResponse_abort(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_abort(data)
        return result, data
        
    def waitForCompletion_abort(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_abort(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_abort()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_abort(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_abort(value)
        return self.waitForCompletion_abort(cmdId, timeoutInSeconds)

    def issueCommand_enable(self, value):
        data = Electrometer_command_enableC()
        data.value = value

        return self.sal.issueCommand_enable(data)

    def getResponse_enable(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_enable(data)
        return result, data
        
    def waitForCompletion_enable(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_enable(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_enable()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_enable(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_enable(value)
        return self.waitForCompletion_enable(cmdId, timeoutInSeconds)

    def issueCommand_disable(self, value):
        data = Electrometer_command_disableC()
        data.value = value

        return self.sal.issueCommand_disable(data)

    def getResponse_disable(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_disable(data)
        return result, data
        
    def waitForCompletion_disable(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_disable(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_disable()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_disable(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_disable(value)
        return self.waitForCompletion_disable(cmdId, timeoutInSeconds)

    def issueCommand_standby(self, value):
        data = Electrometer_command_standbyC()
        data.value = value

        return self.sal.issueCommand_standby(data)

    def getResponse_standby(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_standby(data)
        return result, data
        
    def waitForCompletion_standby(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_standby(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_standby()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_standby(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_standby(value)
        return self.waitForCompletion_standby(cmdId, timeoutInSeconds)

    def issueCommand_exitControl(self, value):
        data = Electrometer_command_exitControlC()
        data.value = value

        return self.sal.issueCommand_exitControl(data)

    def getResponse_exitControl(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_exitControl(data)
        return result, data
        
    def waitForCompletion_exitControl(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_exitControl(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_exitControl()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_exitControl(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_exitControl(value)
        return self.waitForCompletion_exitControl(cmdId, timeoutInSeconds)

    def issueCommand_start(self, settingsToApply):
        data = Electrometer_command_startC()
        data.settingsToApply = settingsToApply

        return self.sal.issueCommand_start(data)

    def getResponse_start(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_start(data)
        return result, data
        
    def waitForCompletion_start(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_start(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_start()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_start(self, settingsToApply, timeoutInSeconds = 10):
        cmdId = self.issueCommand_start(settingsToApply)
        return self.waitForCompletion_start(cmdId, timeoutInSeconds)

    def issueCommand_enterControl(self, value):
        data = Electrometer_command_enterControlC()
        data.value = value

        return self.sal.issueCommand_enterControl(data)

    def getResponse_enterControl(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_enterControl(data)
        return result, data
        
    def waitForCompletion_enterControl(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_enterControl(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_enterControl()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_enterControl(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_enterControl(value)
        return self.waitForCompletion_enterControl(cmdId, timeoutInSeconds)

    def issueCommand_setValue(self, parametersAndValues):
        data = Electrometer_command_setValueC()
        data.parametersAndValues = parametersAndValues

        return self.sal.issueCommand_setValue(data)

    def getResponse_setValue(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_setValue(data)
        return result, data
        
    def waitForCompletion_setValue(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_setValue(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_setValue()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_setValue(self, parametersAndValues, timeoutInSeconds = 10):
        cmdId = self.issueCommand_setValue(parametersAndValues)
        return self.waitForCompletion_setValue(cmdId, timeoutInSeconds)

    def issueCommand_performZeroCalib(self, value):
        data = Electrometer_command_performZeroCalibC()
        data.value = value

        return self.sal.issueCommand_performZeroCalib(data)

    def getResponse_performZeroCalib(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_performZeroCalib(data)
        return result, data
        
    def waitForCompletion_performZeroCalib(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_performZeroCalib(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_performZeroCalib()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_performZeroCalib(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_performZeroCalib(value)
        return self.waitForCompletion_performZeroCalib(cmdId, timeoutInSeconds)

    def issueCommand_setDigitalFilter(self, activateAvgFilter, activateFilter, activateMedFilter):
        data = Electrometer_command_setDigitalFilterC()
        data.activateAvgFilter = activateAvgFilter
        data.activateFilter = activateFilter
        data.activateMedFilter = activateMedFilter

        return self.sal.issueCommand_setDigitalFilter(data)

    def getResponse_setDigitalFilter(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_setDigitalFilter(data)
        return result, data
        
    def waitForCompletion_setDigitalFilter(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_setDigitalFilter(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_setDigitalFilter()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_setDigitalFilter(self, activateAvgFilter, activateFilter, activateMedFilter, timeoutInSeconds = 10):
        cmdId = self.issueCommand_setDigitalFilter(activateAvgFilter, activateFilter, activateMedFilter)
        return self.waitForCompletion_setDigitalFilter(cmdId, timeoutInSeconds)

    def issueCommand_setIntegrationTime(self, intTime):
        data = Electrometer_command_setIntegrationTimeC()
        data.intTime = intTime

        return self.sal.issueCommand_setIntegrationTime(data)

    def getResponse_setIntegrationTime(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_setIntegrationTime(data)
        return result, data
        
    def waitForCompletion_setIntegrationTime(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_setIntegrationTime(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_setIntegrationTime()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_setIntegrationTime(self, intTime, timeoutInSeconds = 10):
        cmdId = self.issueCommand_setIntegrationTime(intTime)
        return self.waitForCompletion_setIntegrationTime(cmdId, timeoutInSeconds)

    def issueCommand_setMode(self, mode):
        data = Electrometer_command_setModeC()
        data.mode = mode

        return self.sal.issueCommand_setMode(data)

    def getResponse_setMode(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_setMode(data)
        return result, data
        
    def waitForCompletion_setMode(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_setMode(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_setMode()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_setMode(self, mode, timeoutInSeconds = 10):
        cmdId = self.issueCommand_setMode(mode)
        return self.waitForCompletion_setMode(cmdId, timeoutInSeconds)

    def issueCommand_setRange(self, setRange):
        data = Electrometer_command_setRangeC()
        data.setRange = setRange

        return self.sal.issueCommand_setRange(data)

    def getResponse_setRange(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_setRange(data)
        return result, data
        
    def waitForCompletion_setRange(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_setRange(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_setRange()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_setRange(self, setRange, timeoutInSeconds = 10):
        cmdId = self.issueCommand_setRange(setRange)
        return self.waitForCompletion_setRange(cmdId, timeoutInSeconds)

    def issueCommand_startScan(self, value):
        data = Electrometer_command_startScanC()
        data.value = value

        return self.sal.issueCommand_startScan(data)

    def getResponse_startScan(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_startScan(data)
        return result, data
        
    def waitForCompletion_startScan(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_startScan(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_startScan()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_startScan(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_startScan(value)
        return self.waitForCompletion_startScan(cmdId, timeoutInSeconds)

    def issueCommand_startScanDt(self, scanDuration):
        data = Electrometer_command_startScanDtC()
        data.scanDuration = scanDuration

        return self.sal.issueCommand_startScanDt(data)

    def getResponse_startScanDt(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_startScanDt(data)
        return result, data
        
    def waitForCompletion_startScanDt(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_startScanDt(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_startScanDt()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_startScanDt(self, scanDuration, timeoutInSeconds = 10):
        cmdId = self.issueCommand_startScanDt(scanDuration)
        return self.waitForCompletion_startScanDt(cmdId, timeoutInSeconds)

    def issueCommand_stopScan(self, value):
        data = Electrometer_command_stopScanC()
        data.value = value

        return self.sal.issueCommand_stopScan(data)

    def getResponse_stopScan(self):
        data = Electrometer_ackcmdC()
        result = self.sal.getResponse_stopScan(data)
        return result, data
        
    def waitForCompletion_stopScan(self, cmdId, timeoutInSeconds = 10):
        waitResult = self.sal.waitForCompletion_stopScan(cmdId, timeoutInSeconds)
        #ackResult, ack = self.getResponse_stopScan()
        #return waitResult, ackResult, ack
        return waitResult
        
    def issueCommandThenWait_stopScan(self, value, timeoutInSeconds = 10):
        cmdId = self.issueCommand_stopScan(value)
        return self.waitForCompletion_stopScan(cmdId, timeoutInSeconds)



    def getNextEvent_settingVersions(self):
        data = Electrometer_logevent_settingVersionsC()
        result = self.sal.getEvent_settingVersions(data)
        return result, data
        
    def getEvent_settingVersions(self):
        return self.getEvent(self.getNextEvent_settingVersions)
        
    def subscribeEvent_settingVersions(self, action):
        self.eventSubscribers_settingVersions.append(action)
        if "event_settingVersions" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingVersions"] = [self.getNextEvent_settingVersions, self.eventSubscribers_settingVersions]

    def getNextEvent_errorCode(self):
        data = Electrometer_logevent_errorCodeC()
        result = self.sal.getEvent_errorCode(data)
        return result, data
        
    def getEvent_errorCode(self):
        return self.getEvent(self.getNextEvent_errorCode)
        
    def subscribeEvent_errorCode(self, action):
        self.eventSubscribers_errorCode.append(action)
        if "event_errorCode" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_errorCode"] = [self.getNextEvent_errorCode, self.eventSubscribers_errorCode]

    def getNextEvent_summaryState(self):
        data = Electrometer_logevent_summaryStateC()
        result = self.sal.getEvent_summaryState(data)
        return result, data
        
    def getEvent_summaryState(self):
        return self.getEvent(self.getNextEvent_summaryState)
        
    def subscribeEvent_summaryState(self, action):
        self.eventSubscribers_summaryState.append(action)
        if "event_summaryState" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_summaryState"] = [self.getNextEvent_summaryState, self.eventSubscribers_summaryState]

    def getNextEvent_appliedSettingsMatchStart(self):
        data = Electrometer_logevent_appliedSettingsMatchStartC()
        result = self.sal.getEvent_appliedSettingsMatchStart(data)
        return result, data
        
    def getEvent_appliedSettingsMatchStart(self):
        return self.getEvent(self.getNextEvent_appliedSettingsMatchStart)
        
    def subscribeEvent_appliedSettingsMatchStart(self, action):
        self.eventSubscribers_appliedSettingsMatchStart.append(action)
        if "event_appliedSettingsMatchStart" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_appliedSettingsMatchStart"] = [self.getNextEvent_appliedSettingsMatchStart, self.eventSubscribers_appliedSettingsMatchStart]

    def getNextEvent_detailedState(self):
        data = Electrometer_logevent_detailedStateC()
        result = self.sal.getEvent_detailedState(data)
        return result, data
        
    def getEvent_detailedState(self):
        return self.getEvent(self.getNextEvent_detailedState)
        
    def subscribeEvent_detailedState(self, action):
        self.eventSubscribers_detailedState.append(action)
        if "event_detailedState" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_detailedState"] = [self.getNextEvent_detailedState, self.eventSubscribers_detailedState]

    def getNextEvent_digitalFilterChange(self):
        data = Electrometer_logevent_digitalFilterChangeC()
        result = self.sal.getEvent_digitalFilterChange(data)
        return result, data
        
    def getEvent_digitalFilterChange(self):
        return self.getEvent(self.getNextEvent_digitalFilterChange)
        
    def subscribeEvent_digitalFilterChange(self, action):
        self.eventSubscribers_digitalFilterChange.append(action)
        if "event_digitalFilterChange" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_digitalFilterChange"] = [self.getNextEvent_digitalFilterChange, self.eventSubscribers_digitalFilterChange]

    def getNextEvent_heartbeat(self):
        data = Electrometer_logevent_heartbeatC()
        result = self.sal.getEvent_heartbeat(data)
        return result, data
        
    def getEvent_heartbeat(self):
        return self.getEvent(self.getNextEvent_heartbeat)
        
    def subscribeEvent_heartbeat(self, action):
        self.eventSubscribers_heartbeat.append(action)
        if "event_heartbeat" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_heartbeat"] = [self.getNextEvent_heartbeat, self.eventSubscribers_heartbeat]

    def getNextEvent_integrationTime(self):
        data = Electrometer_logevent_integrationTimeC()
        result = self.sal.getEvent_integrationTime(data)
        return result, data
        
    def getEvent_integrationTime(self):
        return self.getEvent(self.getNextEvent_integrationTime)
        
    def subscribeEvent_integrationTime(self, action):
        self.eventSubscribers_integrationTime.append(action)
        if "event_integrationTime" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_integrationTime"] = [self.getNextEvent_integrationTime, self.eventSubscribers_integrationTime]

    def getNextEvent_intensity(self):
        data = Electrometer_logevent_intensityC()
        result = self.sal.getEvent_intensity(data)
        return result, data
        
    def getEvent_intensity(self):
        return self.getEvent(self.getNextEvent_intensity)
        
    def subscribeEvent_intensity(self, action):
        self.eventSubscribers_intensity.append(action)
        if "event_intensity" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_intensity"] = [self.getNextEvent_intensity, self.eventSubscribers_intensity]

    def getNextEvent_largeFileObjectAvailable(self):
        data = Electrometer_logevent_largeFileObjectAvailableC()
        result = self.sal.getEvent_largeFileObjectAvailable(data)
        return result, data
        
    def getEvent_largeFileObjectAvailable(self):
        return self.getEvent(self.getNextEvent_largeFileObjectAvailable)
        
    def subscribeEvent_largeFileObjectAvailable(self, action):
        self.eventSubscribers_largeFileObjectAvailable.append(action)
        if "event_largeFileObjectAvailable" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_largeFileObjectAvailable"] = [self.getNextEvent_largeFileObjectAvailable, self.eventSubscribers_largeFileObjectAvailable]

    def getNextEvent_measureRange(self):
        data = Electrometer_logevent_measureRangeC()
        result = self.sal.getEvent_measureRange(data)
        return result, data
        
    def getEvent_measureRange(self):
        return self.getEvent(self.getNextEvent_measureRange)
        
    def subscribeEvent_measureRange(self, action):
        self.eventSubscribers_measureRange.append(action)
        if "event_measureRange" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_measureRange"] = [self.getNextEvent_measureRange, self.eventSubscribers_measureRange]

    def getNextEvent_measureType(self):
        data = Electrometer_logevent_measureTypeC()
        result = self.sal.getEvent_measureType(data)
        return result, data
        
    def getEvent_measureType(self):
        return self.getEvent(self.getNextEvent_measureType)
        
    def subscribeEvent_measureType(self, action):
        self.eventSubscribers_measureType.append(action)
        if "event_measureType" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_measureType"] = [self.getNextEvent_measureType, self.eventSubscribers_measureType]

    def getNextEvent_settingsAppliedReadSets(self):
        data = Electrometer_logevent_settingsAppliedReadSetsC()
        result = self.sal.getEvent_settingsAppliedReadSets(data)
        return result, data
        
    def getEvent_settingsAppliedReadSets(self):
        return self.getEvent(self.getNextEvent_settingsAppliedReadSets)
        
    def subscribeEvent_settingsAppliedReadSets(self, action):
        self.eventSubscribers_settingsAppliedReadSets.append(action)
        if "event_settingsAppliedReadSets" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingsAppliedReadSets"] = [self.getNextEvent_settingsAppliedReadSets, self.eventSubscribers_settingsAppliedReadSets]

    def getNextEvent_settingsAppliedSerConf(self):
        data = Electrometer_logevent_settingsAppliedSerConfC()
        result = self.sal.getEvent_settingsAppliedSerConf(data)
        return result, data
        
    def getEvent_settingsAppliedSerConf(self):
        return self.getEvent(self.getNextEvent_settingsAppliedSerConf)
        
    def subscribeEvent_settingsAppliedSerConf(self, action):
        self.eventSubscribers_settingsAppliedSerConf.append(action)
        if "event_settingsAppliedSerConf" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingsAppliedSerConf"] = [self.getNextEvent_settingsAppliedSerConf, self.eventSubscribers_settingsAppliedSerConf]

    def getNextEvent_deviceErrorCode(self):
        data = Electrometer_logevent_deviceErrorCodeC()
        result = self.sal.getEvent_deviceErrorCode(data)
        return result, data
        
    def getEvent_deviceErrorCode(self):
        return self.getEvent(self.getNextEvent_deviceErrorCode)
        
    def subscribeEvent_deviceErrorCode(self, action):
        self.eventSubscribers_deviceErrorCode.append(action)
        if "event_deviceErrorCode" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_deviceErrorCode"] = [self.getNextEvent_deviceErrorCode, self.eventSubscribers_deviceErrorCode]



