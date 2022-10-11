__all__ = ["execute_csc", "command_csc"]

import asyncio

from lsst.ts import salobj

from .csc import ElectrometerCsc


def execute_csc() -> None:
    asyncio.run(ElectrometerCsc.amain(index=True))


def command_csc() -> None:
    asyncio.run(salobj.CscCommander.amain(name="Electrometer", index=True))
