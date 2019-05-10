# This file is part of Electrometer.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import asyncio
import warnings
import logging
import serial
from numpy import array as nparray
import socket

from lsst.ts.electrometer.electrometerController.ElectrometerControllerSimulator import ElectrometerSimulator
from lsst.ts.electrometer.electrometerController.ElectrometerController import ElectrometerController
import lsst.ts.electrometer.electrometerController.IElectrometerController as iec
import lsst.ts.electrometer.electrometerController.ElectrometerCommands as ecomm

from lsst.ts.pythonFileReader.ConfigurationFileReaderYaml import FileReaderYaml
from lsst.ts.pythonFitsfile.PythonFits import PythonFits
from lsst.ts.salobj import base_csc

try:
    import SALPY_Electrometer
except ImportError:
    warnings.warn(
        "Could not import SALPY_Electrometer; ElectrometerCSC will not work")

VERSION = 1.0


class ElectrometerCsc(base_csc.BaseCsc):
    """Electrometer CSC

    Parameters
    ----------
    index : `int`
        Index of Electrometer component;
    initial_state : `salobj.State`
        The initial state of the CSC. Typically one of:
        - State.ENABLED if you want the CSC immediately usable.
        - State.OFFLINE if you want full emulation of a CSC.

    """
    def __init__(self, index, initial_state=base_csc.State.STANDBY):

        # Configuration initialization
        self.localConfiguration = FileReaderYaml(
            "../settingFiles", "Test", index)
        self.mainConfiguration = FileReaderYaml("../settingFiles", "", "")
        self.mainConfiguration.loadFile("mainSetup")

        # Pre-SAL setup
        self.fitsDirectory = os.path.join(
            str(self.mainConfiguration.readValue('filePath')), f"{index}")
        if not os.path.exists(self.fitsDirectory):
            os.makedirs(self.fitsDirectory)

        self.salId = self.mainConfiguration.readValue('salId')
        self.simulated = self.mainConfiguration.readValue('simulated')

        if initial_state not in base_csc.State:
            raise ValueError(
                f"intial_state={initial_state} is not a salobj.State enum")
        super().__init__(SALPY_Electrometer, self.salId)

        # CSC declarations
        self.summary_state = initial_state

        # Loops
        self.stateCheckLoopfrequency = 0.2
        self.telemetryLoop = 0.2

        # Loggins start
        self.log = logging.getLogger(__name__)
        self.log.debug("logger initialized")
        self.log.info("Electrometer CSC initialized")

        # Events declaration
        self.evt_appliedSettingsMatchStart_data = self.evt_appliedSettingsMatchStart.DataType()
        self.evt_detailedState_data = self.evt_detailedState.DataType()
        self.evt_digitalFilterChange_data = self.evt_digitalFilterChange.DataType()
        self.evt_errorCode_data = self.evt_errorCode.DataType()
        self.evt_integrationTime_data = self.evt_integrationTime.DataType()
        self.evt_intensity_data = self.evt_intensity.DataType()
        self.evt_largeFileObjectAvailable_data = self.evt_largeFileObjectAvailable.DataType()
        self.evt_measureRange_data = self.evt_measureRange.DataType()
        self.evt_measureType_data = self.evt_measureType.DataType()
        self.evt_settingsAppliedReadSets_data = self.evt_settingsAppliedReadSets.DataType()
        self.evt_settingsAppliedSerConf_data = self.evt_settingsAppliedSerConf.DataType()
        self.evt_settingVersions_data = self.evt_settingVersions.DataType()

        # Electrometer declarations
        if(self.simulated == 1):
            self.electrometer = ElectrometerSimulator()
        else:
            self.electrometer = ElectrometerController()
        self.appliedSettingsMatchStart = False
        self.detailed_state = iec.ElectrometerStates.OFFLINESTATE
        self.stop_triggered = False
        self.lastScanTime = 0

        # Loop initialization
        asyncio.ensure_future(self.init_stateLoop())
        asyncio.ensure_future(self.init_intensityLoop())

        # salobj configuration to run the same command mult
        self.cmd_startScanDt.allow_multiple_commands = True
        self.cmd_startScan.allow_multiple_commands = True
        self.cmd_stopScan.allow_multiple_commands = True

    def do_setLogLevel(self):
        pass

    def do_setSimulationMode(self):
        pass

    def do_start(self, id_data):
        """Start the electrometer CSC. It changed the CSC to standby and clear the 
        electrometer controller configuration to start fresh
        """
        self.localConfiguration.setSettingsFromLabel(
            id_data.data.settingsToApply, self.mainConfiguration)
        self.publish_settingVersions(
            self.mainConfiguration.getRecommendedSettings())

        self.apply_serialConfigurationSettings()

        self.apply_initialSetupSettings()

        self.publish_appliedSettingsMatchStart(True)

        self.electrometer.updateState(iec.ElectrometerStates.DISABLEDSTATE)
        super().do_start(id_data)
        self.log.debug("Start done...")

    def do_enterControl(self, id_data):
        """Not used
        """
        pass

    def do_disable(self, id_data):
        """Change state to disabled state
        """
        super().do_disable(id_data)
        self.electrometer.updateState(iec.ElectrometerStates.DISABLEDSTATE)
        self.log.debug("Disable done...")

    def do_standby(self, id_data):
        """Go to standby and disconnect from the controller. After this no communication is possible.
        """
        super().do_standby(id_data)
        self.electrometer.updateState(iec.ElectrometerStates.STANDBYSTATE)
        # Reset value for the next time a start is generated
        self.appliedSettingsMatchStart = False
        try:  # Try to diconnect but if it doesn't work is not a problem....
            self.electrometer.disconnect()
        except:
            self.log.debug("Warning: Error disconnecting device...")
        self.log.debug("Standby done...")

    def do_enable(self, id_data):
        """Enables the CSC and gives full control
        """
        super().do_enable(id_data)
        print("Trying enable")
        self.electrometer.updateState(iec.ElectrometerStates.NOTREADINGSTATE)
        self.log.debug("Enable done...")

    def do_exitControl(self, id_data):
        """Power off the CSC
        """
        super().do_exitControl(id_data)
        self.electrometer.updateState(iec.ElectrometerStates.OFFLINESTATE)
        self.log.debug("exitControl done...")

    async def do_startScanDt(self, id_data):
        """Start storing readings inside the electrometer buffer for a 
        fixed time, this command will change detailedState from NotReadingState 
        to SetDurationReadingState and to stop storing data into the buffer and 
        publish the LFO there are 2 possibilities. Reading during scanDuration
        time input in the command or sending a stopScan command
        """
        self.electrometer.performZeroCorrection()
        values, times, temps, units = await self.electrometer.readDuringTime(id_data.data.scanDuration)
        self.publishLFO_and_createFitsFile(values, times, self.lastScanTime)
        self.log.debug("Start scan DT done...")

    async def do_startScan(self, id_data):
        """Start storing readings inside the electrometer buffer, 
        this command will change detailedState from NotReadingState 
        to ManualReadingState and continues storing data into the buffer. 
        The data will be published to the LFO when stopScan command is 
        received or a timeout occurs (300 seconds)
        """
        self.electrometer.performZeroCorrection()
        self.lastScanTime = self.getCurrentTime()
        self.electrometer.readManual()
        self.log.debug("startScan done...")

    async def do_performZeroCalib(self, id_data):
        """Performs a zero correction in the device. It's recommended 
        to perform this zero correction every time the range changes. 
        The steps taken to perform this comes from the datasheet 
        6517B-901-01 Rev. B / June 2009 under Zero correct. It is as 
        following. 1- Enable Zero check, 2- Set unit to read, 3- Set 
        range to measure 4- Enable Zero Correction 5- Disable Zero 
        check. For unit and range, it uses the last values selected, 
        either via command or from the configuration file
        """
        self.electrometer.performZeroCorrection()
        self.log.debug("performZeroCalib done...")

    async def do_setDigitalFilter(self, id_data):
        """Configure the digital filter inside the Electrometer 
        controller. Be aware that activating any filters will reduce
        the number of readings per second the device will be able to 
        handle
        """
        self.publish_appliedSettingsMatchStart(False)
        self.electrometer.activateMedianFilter(id_data.data.activateMedFilter)
        self.electrometer.activateAverageFilter(id_data.data.activateAvgFilter)
        self.electrometer.activateFilter(id_data.data.activateFilter)
        self.publish_digitalFilterChange(self.electrometer.getAverageFilterStatus(
        ), self.electrometer.getFilterStatus(), self.electrometer.getMedianFilterStatus())
        self.log.debug("setDigitalFilter done...")

    async def do_setIntegrationTime(self, id_data):
        """This is the length of time for a given sample from the 
        electrometer, however, due to the time it takes to read the 
        buffer and process the data, this is not the rate at which 
        samples are taken
        """
        self.publish_appliedSettingsMatchStart(False)
        self.electrometer.setIntegrationTime(id_data.data.intTime)
        self.publish_integrationTime(self.electrometer.getIntegrationTime())
        self.log.debug("setIntegrationTime done...")

    async def do_setMode(self, id_data):
        """Set unit to measure, the possibilities are: Current, 
        Voltage, Charge or Resistance
        """
        self.publish_appliedSettingsMatchStart(False)
        self.electrometer.setMode(self.SalModeToDeviceMode(id_data.data.mode))
        self.publish_measureType(self.electrometer.getMode())
        self.log.debug("setMode done...")

    async def do_setRange(self, id_data):
        """Set measurement range, it will use the current
        unit selected
        """
        self.publish_appliedSettingsMatchStart(False)
        self.electrometer.setRange(id_data.data.setRange)
        self.publish_measureRange(self.electrometer.getRange())
        self.log.debug("setRange done...")

    async def do_stopScan(self, id_data):
        """Command to stop a current reading process, when it
        finishes stopping the process it will read the data 
        from the buffer and will publish the LFO event
        """
        values, times = await self.electrometer.stopReading()
        self.publishLFO_and_createFitsFile(values, times, self.lastScanTime)
        self.log.debug("stopScan done...")

    async def init_stateLoop(self):
        """Initialize the looop to check if the detailedSate has
        changed in the device
        """
        while True:
            self.update_deviceState(self.electrometer.getState())
            await asyncio.sleep(self.stateCheckLoopfrequency)

    async def init_intensityLoop(self):
        """Initialize loop to publish electrometer intensity values
        when in ReadingState
        """
        while True:
            try:
                if(self.electrometer.getState() == iec.ElectrometerStates.MANUALREADINGSTATE or self.electrometer.getState() == iec.ElectrometerStates.DURATIONREADINGSTATE):
                    value, temperature, temperature, unit = self.electrometer.getValue()
                    self.publish_intensity(value, unit)
            except ValueError as e:
                print("Error intensity loop:"+e)
            await asyncio.sleep(self.telemetryLoop)

    def publish_appliedSettingsMatchStart(self, value):
        """Publish appliedSettingsMatchStart when 
        if it has changed. If not, do nothing.
        Arguments:
            value {bool} -- True if settings are from configuration files
                            False if any of the configuration has changed 
                            via SAL command
        """
        if(value == self.appliedSettingsMatchStart):
            pass
        else:
            self.evt_appliedSettingsMatchStart_data.appliedSettingsMatchStartIsTrue = value
            self.evt_appliedSettingsMatchStart.put(
                self.evt_appliedSettingsMatchStart_data)
            self.appliedSettingsMatchStart = value

    def publish_intensity(self, value, unit):
        """Publish value measured from the photodione in the unit set from setMode

        Arguments:
            value {float} -- Measurement from the photodiode
            unit {long} --  mode currently configured. Current, 
                            Voltage, Charge or Resistance
        """
        self.evt_intensity_data.intensity = value
        self.evt_intensity_data.unit = unit
        self.evt_intensity_data.timestamp = self.getCurrentTime()
        self.evt_intensity.put(self.evt_intensity_data)

    def publish_measureRange(self, value):
        """Publish the range currently configured
        inside the electrometer

        Arguments:
            value {float} -- -1 for automatic range. Volts range from 0 to 210 Volts,
                              Current range from 0 to 21e-3 Amps, Resistance from 0 
                              to 100e18 Ohms, Charge from 0 to +2.1e-6 Coulombs
        """
        self.evt_measureRange_data = self.evt_measureRange.DataType()
        self.evt_measureRange_data.rangeValue = value
        self.evt_measureRange.put(self.evt_measureRange_data)

    def publish_measureType(self, mode):
        """Publish when the type of measurment has changed
        
        Arguments:
            mode {long} -- mode currently configured. Current, 
                            Voltage, Charge or Resistance
        """
        modeToPublish = self.devideModeToSalMode(mode)
        self.evt_measureType_data = self.evt_measureType.DataType()
        self.evt_measureType_data.mode = modeToPublish
        self.evt_measureType.put(self.evt_measureType_data)

    def devideModeToSalMode(self, mode):
        """Convert the internal mode to the SAL enum mode.

        Arguments:
            mode {UnitMode} -- UnitMode Enumeration for:
            Current, Voltage, Charge or Resistance

        Raises:
            ValueError: Raise exception if value doesn't exist

        Returns:
            [long] -- SAL enum mode
        """
        if(mode == ecomm.UnitMode.CURR):
            modeToPublish = SALPY_Electrometer.Electrometer_shared_UnitToRead_Current
        elif(mode == ecomm.UnitMode.CHAR):
            modeToPublish = SALPY_Electrometer.Electrometer_shared_UnitToRead_Charge
        else:
            raise ValueError(f"Unit {mode} not implemented")
        return modeToPublish

    def SalModeToDeviceMode(self, mode):
        """Convert the SAL enumeration mode to the internal UnitMode enum.

        Arguments:
            mode {UnitToRead} -- SAL UnitToRead Enuneration

        Raises:
            ValueError:  Raise exception if value doesn't exist

        Returns:
            [UnitMode] -- UnitMode enumeration
        """
        deviceMode = ecomm.UnitMode.CURR

        if(mode == SALPY_Electrometer.Electrometer_shared_UnitToRead_Current):
            deviceMode = ecomm.UnitMode.CURR
        elif(mode == SALPY_Electrometer.Electrometer_shared_UnitToRead_Charge):
            deviceMode = ecomm.UnitMode.CHAR
        else:
            raise ValueError(f"Unit {mode} not implemented")
        return deviceMode

    def publish_integrationTime(self, integrationTime):
        """Publish integration time event with value from input

        Arguments:
            integrationTime {float} -- Integration rate in seconds it should be 
            between the range (166.67e-6 to 200e-3)
        """
        self.evt_integrationTime_data = self.evt_integrationTime.DataType()
        self.evt_integrationTime_data.intTime = integrationTime
        self.evt_integrationTime.put(self.evt_integrationTime_data)

    def publish_digitalFilterChange(self, activateAvgFilter, activateFilter, activateMedFilter):
        """Publish digital filter status 
        
        Arguments:
            activateAvgFilter {bool} -- Average digital filter status inside the electrometer, 
            it uses the Default value inside the device (last 10 readings) to do the average 
            calculation, true for ON and False for 0
            activateFilter {bool} -- Digital Filter configuration. If this is 0, none of the filters will operate
            activateMedFilter {bool} -- The median filter is used to determine the “middle-most” reading from a 
            group of readings that are arranged according to size. Activate the median filter inside the electrometer, true for ON 1 False for 0
        """
        self.evt_digitalFilterChange_data = self.evt_digitalFilterChange.DataType()
        self.evt_digitalFilterChange_data.activateAverageFilter = activateAvgFilter
        self.evt_digitalFilterChange_data.activateFilter = activateFilter
        self.evt_digitalFilterChange_data.activateMedianFilter = activateMedFilter
        self.evt_digitalFilterChange.put(self.evt_digitalFilterChange_data)

    def update_deviceState(self, newState):
        """Update the device state, this is the same as the DetailedState

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
        if(newState == self.detailed_state):
            return
        self.detailed_state = self.electrometer.getState()
        if(self.detailed_state == iec.ElectrometerStates.DISABLEDSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_DisabledState
        elif(self.detailed_state == iec.ElectrometerStates.ENABLEDSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_EnabledState
        elif(self.detailed_state == iec.ElectrometerStates.FAULTSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_FaultState
        elif(self.detailed_state == iec.ElectrometerStates.OFFLINESTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_OfflineState
        elif(self.detailed_state == iec.ElectrometerStates.STANDBYSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_StandbyState
        elif(self.detailed_state == iec.ElectrometerStates.MANUALREADINGSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_ManualReadingState
        elif(self.detailed_state == iec.ElectrometerStates.DURATIONREADINGSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_SetDurationReadingState
        elif(self.detailed_state == iec.ElectrometerStates.CONFIGURINGSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_ConfiguringState
        elif(self.detailed_state == iec.ElectrometerStates.NOTREADINGSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_NotReadingState
        elif(self.detailed_state == iec.ElectrometerStates.READINGBUFFERSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_ReadingBufferState
        self.evt_detailedState.put(self.evt_detailedState_data)

    def getCurrentTime(self):
        """get current time from salobj
        
        Returns:
            double -- timestamp from salObj
        """
        return self.salinfo.manager.getCurrentTime()

    def publishLFO_and_createFitsFile(self, values, times, readStartTime):
        """Created the fits file with the info and announce it via largeFileObjectAvailable
        event
        
        Arguments:
            values {float array} -- Array with the data from the measurements 
            from the electrometer buffer
            times {float array} -- time when the measurement was taken
            readStartTime {float} -- Initial time when the scan command was executed
        """
        dataArray = nparray([times, values])
        name = str(self.salId) + "-" + str(self.getCurrentTime())
        fitsFile = PythonFits(self.fitsDirectory, name, separator='/')
        fitsFile.addData(dataArray)
        fitsFile.addHeader("CLMN1", "Time", "Time in seconds")
        fitsFile.addHeader("CLMN2", "Intensity", "")
        fitsFile.addHeader("HWINFO", self.electrometer.getHardwareInfo(), "")

        errorListCode, errorListName = self.electrometer.getErrorList()
        fitsFile.addHeader("DERROR", ','.join(
            map(str, errorListCode)), "Device error list")  # To be implemented

        fitsFile.addHeader("ITIME", readStartTime, "Start time")
        fitsFile.addHeader("ITEMP", self.electrometer.getLastScanValues()[
                           0][0], "Initial temperature")
        fitsFile.addHeader("ETEMP", self.electrometer.getLastScanValues()[
                           1][0], "End temperature")
        fitsFile.addHeader("IUNIT", self.electrometer.getLastScanValues()[
                           0][1], "Mode read")

        fitsFile.saveToFile()
        fitsFile.closeFile()
        checksum = fitsFile.getChecksum()
        size = fitsFile.getFileSize()

        url = "http://" + self.mainConfiguration.readValue('httpHost') + ":" + str(self.mainConfiguration.readValue('port')) + "/" + name + ".fits"
        generator = "electrometer" + str(self.salId)
        version = float(VERSION)
        checkSum = str(checksum)
        mimeType = "electrometer"
        byteSize = size
        salId = str(self.salId)

        self.publish_largeFileObjectAvailable(
            url, generator, version, checkSum, mimeType, byteSize, salId)

    def publish_largeFileObjectAvailable(self, url, generator, version, checkSum, mimeType, byteSize, salId):
        """Publish the largeFileObjectAvailable to announce to the EFD that there is a new file available

        Arguments:
            url {string} --  Uniform Resource Locator which links to a Large File Object
                             either for ingest into the EFD Large File Annex, or to announce
                             the successful copy of same to the EFD Large File Annex.
                             Protocols are those supported by the cURL library.
            generator {string} -- Name of the package which generated the file being announced
            version {float} -- A dotted x.y version number denoting the file format revision
            checkSum {string} -- Hexadecimal character string holding the checksum of the file
            mimeType {string} -- Mime Type code for the file
            byteSize {long} -- Size of file in bytes
            salId {string} -- A generic identifier field
        """
        self.evt_largeFileObjectAvailable_data.url = url
        self.evt_largeFileObjectAvailable_data.generator = generator
        self.evt_largeFileObjectAvailable_data.version = version
        self.evt_largeFileObjectAvailable_data.checkSum = checkSum
        self.evt_largeFileObjectAvailable_data.mimeType = mimeType
        self.evt_largeFileObjectAvailable_data.byteSize = byteSize
        self.evt_largeFileObjectAvailable_data.id = salId

        self.evt_largeFileObjectAvailable.put(
            self.evt_largeFileObjectAvailable_data)

    def publish_settingsAppliedReadSets(self, filterActive, avgFilterActive, inputRange, integrationTime, medianFilterActive, mode):
        """Publish settingsAppliedReadSets, this is the inital setup of the 
        electrometer when starting the CSC

        Arguments:
            filterActive {bool} -- Digital Filter configuration. If this is OFF, none of the filters will operate
            avgFilterActive {bool} -- Average digital filter status inside the electrometer, it uses the Default value 
                                      inside the device (last 10 readings) to do the average calculation, true for ON 
                                      and False for OFF
            inputRange {double} -- Ranges use to read values from the photodiode using the current Mode. -1 for automatic
                                   range. Volts range from 0 to 210V, Current range from 0 to 21e-3Amps, Resistance from 0
                                   to 100e18, Charge from 0 to +2.1e-6
            integrationTime {double} -- Integration rate, this will directly affect reading rates but reading
                                        rates are not going to be the same as reading rates
            medianFilterActive {bool} -- The median filter is used to determine the “middle-most” reading from a 
                                         group of readings that are arranged according to size. Activate the 
                                         median filter inside the electrometer, true for ON and False for OFF
            mode {long} -- Mode used in the configuration file, 0-Current, 1-Charge, 2-Voltage, 3-Resistance
        """
        self.evt_settingsAppliedReadSets_data.filterActive = filterActive
        self.evt_settingsAppliedReadSets_data.avgFilterActive = avgFilterActive
        self.evt_settingsAppliedReadSets_data.inputRange = inputRange
        self.evt_settingsAppliedReadSets_data.integrationTime = integrationTime
        self.evt_settingsAppliedReadSets_data.medianFilterActive = medianFilterActive
        self.evt_settingsAppliedReadSets_data.mode = mode
        self.evt_settingsAppliedReadSets.put(
            self.evt_settingsAppliedReadSets_data)

    def publish_settingsAppliedSerConf(self, visaResource, baudRate, parity, dataBits, stopBits, timeout, termChar, xonxoff, dsrdtr, bytesToRead):
        """Publish settingsAppliedSerConf event to announce the 
        serial configuration event that it is used by the CSC
        
        Arguments:
            visaResource {string} -- Visa resource or port
            baudRate {long} -- Baud rate as a number. allowed values are: 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200
            parity {long} -- Parity checking. PARITY_NONE=0, PARITY_EVEN=1, PARITY_ODD=2, PARITY_MARK=3, PARITY_SPACE=4
            dataBits {long} -- Number of data bits. Possible values: 5, 6, 7, 8
            stopBits {long} -- Number of stop bits. Possible values: 1, 2 
            timeout {float} -- time out in seconds
            termChar {string} -- termination char, endl for end line
            xonxoff {bool} -- Software flow control
            dsrdtr {bool} -- hardware (DSR/DTR) flow control
            bytesToRead {long} -- The maximum amount of bytes to read
        """
        self.evt_settingsAppliedSerConf_data.visaResource = visaResource
        self.evt_settingsAppliedSerConf_data.baudRate = baudRate
        self.evt_settingsAppliedSerConf_data.parity = parity
        self.evt_settingsAppliedSerConf_data.dataBits = dataBits
        self.evt_settingsAppliedSerConf_data.stopBits = stopBits
        self.evt_settingsAppliedSerConf_data.xonxoff = xonxoff
        self.evt_settingsAppliedSerConf_data.dsrdtr = dsrdtr
        self.evt_settingsAppliedSerConf_data.timeout = timeout
        self.evt_settingsAppliedSerConf_data.termChar = termChar
        self.evt_settingsAppliedSerConf_data.bytesToRead = bytesToRead
        self.evt_settingsAppliedSerConf.put(
            self.evt_settingsAppliedSerConf_data)

    def publish_settingVersions(self, recommendedSettingsVersion):
        self.evt_settingVersions_data.recommendedSettingsVersion = recommendedSettingsVersion
        self.evt_settingVersions.put(self.evt_settingVersions_data)

    def apply_serialConfigurationSettings(self):
        """Load serial configuration from file. The set of configuration files paths are 
        obtained from the last settingsApplied attribute in the start command
        """
        self.localConfiguration.loadFile("serialConfiguration")
        port = self.localConfiguration.readValue('port')
        baudrate = self.localConfiguration.readValue('baudrate')
        parity = self.localConfiguration.readValue('parity')
        stopBits = self.localConfiguration.readValue('stopBits')
        dataBits = self.localConfiguration.readValue('byteSize')
        byteToRead = self.localConfiguration.readValue('byteToRead')
        timeout = self.localConfiguration.readValue('timeout')
        xonxoff = self.localConfiguration.readValue('xonxoff')
        dsrdtr = self.localConfiguration.readValue('dsrdtr')
        termChar = self.localConfiguration.readValue('termChar')
        termCharVal = '\n' if termChar == "endl" else '\r'

        if(parity == 0):
            parityVal = serial.PARITY_NONE
        elif(parity == 1):
            parityVal = serial.PARITY_EVEN
        elif(parity == 2):
            parityVal = serial.PARITY_ODD
        elif(parity == 3):
            parityVal = serial.PARITY_MARK
        else:
            parityVal = serial.PARITY_SPACE

        self.electrometer.configureCommunicator(port=port, baudrate=baudrate, parity=parityVal, byteToRead=byteToRead,
                                                stopbits=stopBits, bytesize=dataBits, xonxoff=xonxoff, dsrdtr=dsrdtr, timeout=timeout, termChar=termCharVal)

        self.publish_settingsAppliedSerConf(visaResource=port, baudRate=baudrate, parity=parity, dataBits=dataBits,
                                            stopBits=stopBits, timeout=timeout, termChar=termChar, xonxoff=xonxoff, dsrdtr=dsrdtr, bytesToRead=byteToRead)

    def apply_initialSetupSettings(self):
        """Applies the initial configuration to the electrometer in the following order
        1.- Reset the device configuration
        2.- Configure the mode
        3.- Configure the filter
        4.- Set the range
        5.- Set the integration time
        6.- Disable temperature sensor to increase the number of readings per second
        7.- Publish filter status
        8.- Publish mode
        9.- Publish range
        10.- Publish integration time
        11.- Publish settingsApplied
        """
        self.localConfiguration.loadFile("initialElectrometerSetup")
        mode = self.localConfiguration.readValue('mode')
        range_v = self.localConfiguration.readValue('range')
        integrationTime = self.localConfiguration.readValue('integrationTime')
        medianFilterActive = self.localConfiguration.readValue(
            'medianFilterActive')
        filterActive = self.localConfiguration.readValue('filterActive')
        avgFilterActive = self.localConfiguration.readValue('avgFilterActive')

        filterActiveIsActive = (filterActive == 1)
        avgFilterActiveIsActive = (avgFilterActive == 1)
        medianFilterActiveIsActive = (medianFilterActive == 1)

        self.electrometer.resetDevice()
        asyncio.sleep(0)
        self.electrometer.setMode(
            self.SalModeToDeviceMode(mode), skipState=True)
        asyncio.sleep(0)
        self.electrometer.activateFilter(filterActiveIsActive, skipState=True)
        asyncio.sleep(0)
        self.electrometer.setRange(range_v, skipState=True)
        asyncio.sleep(0)
        self.electrometer.setIntegrationTime(integrationTime, skipState=True)
        asyncio.sleep(0)
        self.electrometer.enableTemperatureSensor(enable=False)
        asyncio.sleep(0)
        self.electrometer.disableAll()
        asyncio.sleep(0)

        self.publish_digitalFilterChange(self.electrometer.getAverageFilterStatus(),
                                         self.electrometer.getFilterStatus(), self.electrometer.getMedianFilterStatus())
        asyncio.sleep(0)
        self.publish_measureType(self.electrometer.getMode())
        asyncio.sleep(0)
        self.publish_measureRange(self.electrometer.getRange())
        asyncio.sleep(0)
        self.publish_integrationTime(self.electrometer.getIntegrationTime())
        asyncio.sleep(0)

        self.publish_settingsAppliedReadSets(
            filterActiveIsActive, avgFilterActiveIsActive, range_v, integrationTime, medianFilterActiveIsActive, mode)
