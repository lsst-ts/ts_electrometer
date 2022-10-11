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
    """Resolution"""


class Filter(enum.IntEnum):
    """The type of filters"""

    MED = 1
    """Median filter"""
    AVER = 2
    """Average filter"""


class Source(str, enum.Enum):
    IMM = "imm"
    TIM = "tim"


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
