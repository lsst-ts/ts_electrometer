from electrometerCSC.ElectrometerCSC import MtAtElectrometerCsc
import SALPY_MtAtElectrometer
import asyncio
import salobj.python.salobj as salobj

csc = MtAtElectrometerCsc(1, salobj.State.STANDBY)

loop = asyncio.get_event_loop()

try:
    loop.run_forever()
except KeyboardInterrupt as e:
    print('Stopping CSC.')
finally:
    loop.close()