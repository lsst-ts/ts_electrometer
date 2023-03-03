# This file is part of ts_electrometer.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site System.
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

import enum


class UnitMode(str, enum.Enum):
    """The units for the electrometer."""

    CURR = "CURR"
    """Current"""

    CHAR = "CHAR"
    """Charge"""

    VOLT = "VOLT"
    """Voltage"""

    RES = "RES"
    """Resistance"""


class Filter(enum.IntEnum):
    """The type of filters"""

    MED = 1
    """Median filter"""
    AVER = 2
    """Average filter"""


class Source(str, enum.Enum):
    """Controls the source setting for triggering data to the buffer."""

    IMM = "imm"
    """Write to buffer immediately"""

    TIM = "tim"
    """Write to buffer on a timer"""


class AverFilterType(enum.IntEnum):
    """The type of average filters."""

    NONE = 1
    """No algorithm applied"""

    SCAL = 2
    """A scaling algorithm"""

    ADV = 3
    """Another type of algorithm."""


class ReadingOption(enum.IntEnum):
    """The type of data reading."""

    LATEST = 1
    """Get the latest reading"""

    NEWREAD = 2
    """Get a new reading"""


class Error(enum.IntEnum):
    FILE_ERROR = 1
    """File failed to write properly."""
