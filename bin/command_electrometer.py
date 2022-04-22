#!/bin/env python

import asyncio
from lsst.ts import salobj

asyncio.run(salobj.CscCommander.amain(name="Electrometer", index=True))
