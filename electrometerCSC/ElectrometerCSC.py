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
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import warnings
import logging
from electrometerController.ElectrometerControllerSimulator import ElectrometerSimulator
import electrometerController.IElectrometerController as iec

try:
    import SALPY_Electrometer
except ImportError:
    warnings.warn("Could not import SALPY_Electrometer; ElectrometerCSC will not work")
from salobj.python.salobj import base_csc

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
        if initial_state not in base_csc.State:
            raise ValueError(f"intial_state={initial_state} is not a salobj.State enum")
        super().__init__(SALPY_Electrometer, index)
        self.summary_state = initial_state
        self.stop_triggered = False

        self.log = logging.getLogger(__name__)
        self.log.debug("logger initialized")
        self.log.info("Electrometer CSC initialized")

        self.evt_appliedSettingsMatchStart_data = self.evt_appliedSettingsMatchStart.DataType()
        self.evt_detailedState_data = self.evt_detailedState.DataType()
        self.evt_digitalFilterChange_data = self.evt_digitalFilterChange.DataType()
        self.evt_errorCode_data = self.evt_errorCode.DataType()
        self.evt_integrationTime_data = self.evt_integrationTime.DataType()
        self.evt_intensity_data = self.evt_intensity.DataType()
        self.evt_largeFileObjectAvailable_data = self.evt_largeFileObjectAvailable.DataType()
        self.evt_measureRange_data = self.evt_measureRange.DataType()
        self.evt_measureType_data = self.evt_measureType.DataType()
        self.evt_rejectedCommand_data = self.evt_rejectedCommand.DataType()
        self.evt_settingsAppliedReadSets_data = self.evt_settingsAppliedReadSets.DataType()
        self.evt_settingsAppliedSerConf_data = self.evt_settingsAppliedSerConf.DataType()
        self.evt_settingVersions_data = self.evt_settingVersions.DataType()

        self.electrometer = ElectrometerSimulator()
        self.appliedSettingsMatchStart = False

    def do_start(self, id_data):
        super().do_start(id_data)
        self.publish_appliedSettingsMatchStart(True)
        self.electrometer.updateState(iec.ElectrometerStates.DISABLEDSTATE)
        print("Start done...")

    def do_disable(self, id_data):
        super().do_disable(id_data)
        print("Disable done...")

    def do_standby(self, id_data):
        super().do_standby(id_data)
        self.appliedSettingsMatchStart = False #Reset value for the next time a start is generated
        print("Standby done...")

    def do_enable(self, id_data):
        super().do_enable(id_data)
        print("Enable done...")

    def do_enable(self, id_data):
        super().do_enable(id_data)
        print("Enable done...")

    def do_exitControl(self, id_data):
        super().do_exitControl(id_data)
        print("exitControl done...")

    def do_startScanDt(self, id_data):
        self.log.debug("Start scan DT done...")

    def do_startScan(self, id_data):
        self.log.debug("startScan done...")

    def do_performZeroCalib(self, id_data):
	
        self.electrometer.performZeroCorrection()
        self.log.debug("performZeroCalib done...")

    def do_setDigitalFilter(self, id_data):
        self.publish_appliedSettingsMatchStart(False)
        self.log.debug("setDigitalFilter done...")

    def do_setIntegrationTime(self, id_data):
        self.publish_appliedSettingsMatchStart(False)
        self.electrometer.setIntegrationTime(id_data.data.intTime)
        self.log.debug("setIntegrationTime done...")

    def do_setMode(self, id_data):
        self.publish_appliedSettingsMatchStart(False)
        self.log.debug("setMode done...")

    def do_setRange(self, id_data):
        self.publish_appliedSettingsMatchStart(False)
        self.log.debug("setRange done...")

    def do_stopScan(self, id_data):
        self.log.debug("stopScan done...")

    def publish_appliedSettingsMatchStart(self, value):
        if(value == self.appliedSettingsMatchStart):
            pass
        else:
            self.evt_appliedSettingsMatchStart_data.appliedSettingsMatchStartIsTrue = value
            self.evt_appliedSettingsMatchStart.put(self.evt_appliedSettingsMatchStart_data)
            self.appliedSettingsMatchStart = value

    def update_deviceState(self, newState):
        if(self.electrometer.getState() == iec.ElectrometerStates.DISABLEDSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_DisabledState
        elif(self.electrometer.getState() == iec.ElectrometerStates.ENABLEDSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_EnabledState
        elif(self.electrometer.getState() == iec.ElectrometerStates.FAULTSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_FaultState
        elif(self.electrometer.getState() == iec.ElectrometerStates.OFFLINESTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_OfflineState
        elif(self.electrometer.getState() == iec.ElectrometerStates.STANDBYSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_StandbyState
        elif(self.electrometer.getState() == iec.ElectrometerStates.MANUALREADINGSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_EnabledState  #Fix after XML update
        elif(self.electrometer.getState() == iec.ElectrometerStates.DURATIONREADINGSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_EnabledState #Fix after XML update
        elif(self.electrometer.getState() == iec.ElectrometerStates.CONFIGURINGSTATE):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_ConfiguringState
        elif(self.electrometer.getState() == iec.ElectrometerStates.NOTREADING):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_EnabledState #Fix after XML update
        elif(self.electrometer.getState() == iec.ElectrometerStates.READINGBUFFER):
            self.evt_detailedState_data.detailedState = SALPY_Electrometer.Electrometer_shared_DetailedState_EnabledState #Fix after XML update
        self.evt_detailedState.put(self.evt_detailedState_data)
