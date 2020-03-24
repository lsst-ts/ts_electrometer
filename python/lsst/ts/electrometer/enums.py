import enum


class UnitMode(enum.IntEnum):
    CURR = 1
    CHAR = 2
    VOLT = 3
    RES = 4


class Filter(enum.IntEnum):
    MED = 1
    AVER = 2


class AverFilterType(enum.IntEnum):
    NONE = 1
    SCAL = 2
    ADV = 3


class readingOption(enum.IntEnum):
    LATEST = 1
    NEWREAD = 2
