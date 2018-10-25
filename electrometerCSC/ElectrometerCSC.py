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

__all__ = ["MtAtElectrometerCsc"]

import asyncio
import warnings

try:
    import SALPY_MtAtElectrometer
except ImportError:
    warnings.warn("Could not import SALPY_MtAtElectrometer; MtAtElectrometerCsc will not work")
from salobj.python.salobj import base_csc

class MtAtElectrometerCsc(base_csc.BaseCsc):
    """Electrometer CSC

    Parameters
    ----------
    index : `int`
        Index of MtAtElectrometer component;
    initial_state : `salobj.State`
        The initial state of the CSC. Typically one of:
        - State.ENABLED if you want the CSC immediately usable.
        - State.OFFLINE if you want full emulation of a CSC.

    """
    def __init__(self, index, initial_state=base_csc.State.STANDBY):
        if initial_state not in base_csc.State:
            raise ValueError(f"intial_state={initial_state} is not a salobj.State enum")
        super().__init__(SALPY_MtAtElectrometer, index)
        self.summary_state = initial_state
        self.stop_triggered = False
        self.log.debug("logger initialized")
        self.log.info("Electrometer CSC initialized")

    def do_startScanDt(self, id_data):
        print("Start scan DT done...")

    def do_startScan(self, id_data):
        print("startScan done...")

    def do_performZeroCalib(self, id_data):
        print("performZeroCalib done...")

    def do_setDigitalFilter(self, id_data):
        print("setDigitalFilter done...")

    def do_setIntegrationTime(self, id_data):
        print("setIntegrationTime done...")

    def do_setMode(self, id_data):
        print("setMode done...")

    def do_setRange(self, id_data):
        print("setRange done...")

    def do_stopScan(self, id_data):
        print("stopScan done...")
