from electrometerCSC.ElectrometerCSC import ElectrometerCsc
import salobj.python.lsst.ts.salobj as salobj
import SALPY_Electrometer

csc = ElectrometerCsc(1, salobj.State.STANDBY)

csc.main(sallib=SALPY_Electrometer, index=1)