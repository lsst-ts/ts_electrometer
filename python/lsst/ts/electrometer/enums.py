import enum


class UnitMode(enum.IntEnum):
    """The units for the electrometer.
    """
    CURR = 1
    """Current"""
    CHAR = 2
    """Charge"""
    VOLT = 3
    """Voltage"""
    RES = 4
    """Resolution"""


class Filter(enum.IntEnum):
    """The type of filters
    """
    MED = 1
    """Median filter"""
    AVER = 2
    """Average filter"""


class AverFilterType(enum.IntEnum):
    """The type of average filters.
    """
    NONE = 1
    """No algorithm applied"""
    SCAL = 2
    """A scaling algorithm"""
    ADV = 3
    """Another type of algorithm."""


class ReadingOption(enum.IntEnum):
    """The type of data reading.
    """
    LATEST = 1
    """Get the latest reading"""
    NEWREAD = 2
    """Get a new reading"""
