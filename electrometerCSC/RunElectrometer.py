from electrometerCSC.ElectrometerCSC import ElectrometerCsc
import asyncio
import salobj.python.salobj as salobj

csc = ElectrometerCsc(1, salobj.State.STANDBY)

loop = asyncio.get_event_loop()

try:
    loop.run_forever()
except KeyboardInterrupt as e:
    print('Stopping CSC.')
finally:
    loop.close()
