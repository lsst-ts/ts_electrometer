import asyncio
from lsst.ts.electrometer.csc import ElectrometerCsc


version = 0.10

asyncio.run(ElectrometerCsc.main(index=True))
