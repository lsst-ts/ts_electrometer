__all__ = ["execute_csc", "command_csc"]

import asyncio

from lsst.ts import salobj

from . import ElectrometerCsc


def execute_csc():
    asyncio.run(ElectrometerCsc.amain(index=True))


def command_csc():
    asyncio.run(salobj.CscCommander.amain(name="Electrometer", index=True))
