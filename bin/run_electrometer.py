#!/bin/env python
import asyncio

from lsst.ts.electrometer.csc import ElectrometerCsc

asyncio.run(ElectrometerCsc.amain(index=True))
