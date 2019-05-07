import unittest
import ElectrometerCommands as ec

class TestFilterCommands(unittest.TestCase):

    def setUp(self):
        self.electrometerController = ec.ElectrometerCommand()

    #Test activate filter command
    def test_activeFilter(self):
        command = self.electrometerController.activateFilter(ec.UnitMode.CURR, ec.Filter.AVER, True)
        expectedResult = ":SENS:CURR:AVER:STAT 1;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.activateFilter(ec.UnitMode.CHAR, ec.Filter.AVER, True)
        expectedResult = ":SENS:CHAR:AVER:STAT 1;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.activateFilter(ec.UnitMode.CHAR, ec.Filter.MED, True)
        expectedResult = ":SENS:CHAR:MED:STAT 1;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.activateFilter(ec.UnitMode.CURR, ec.Filter.MED, False)
        expectedResult = ":SENS:CURR:MED:STAT 0;"
        self.assertEqual(command, expectedResult)

    def test_getAvgFilterStatus(self):
        command = self.electrometerController.getAvgFilterStatus(ec.UnitMode.CURR)
        expectedResult = ":SENS:CURR:AVER:TYPE?;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.getAvgFilterStatus(ec.UnitMode.CHAR)
        expectedResult = ":SENS:CHAR:AVER:TYPE?;"
        self.assertEqual(command, expectedResult)

    def test_getFilterStatus(self):
        command = self.electrometerController.getFilterStatus(ec.UnitMode.CURR, ec.Filter.AVER)
        expectedResult = ":SENS:CURR:AVER:STAT?;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.getFilterStatus(ec.UnitMode.CHAR, ec.Filter.MED)
        expectedResult = ":SENS:CHAR:MED:STAT?;"
        self.assertEqual(command, expectedResult)

    def test_getMedFilterStatus(self):
        command = self.electrometerController.getMedFilterStatus(ec.UnitMode.CURR)
        expectedResult = ":SENS:CURR:MED:STAT?;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.getMedFilterStatus(ec.UnitMode.CHAR)
        expectedResult = ":SENS:CHAR:MED:STAT?;"
        self.assertEqual(command, expectedResult)

    def test_setMedFilterStatus(self):
        command = self.electrometerController.setMedFilterStatus(ec.UnitMode.CURR, True)
        expectedResult = ":SENS:CURR:MED:STAT 1;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setMedFilterStatus(ec.UnitMode.CHAR, False)
        expectedResult = ":SENS:CHAR:MED:STAT 0;"
        self.assertEqual(command, expectedResult)

    def test_setAvgFilterStatus(self):
        command = self.electrometerController.setAvgFilterStatus(ec.UnitMode.CURR, ec.AverFilterType.ADV)
        expectedResult = ":SENS:CURR:AVER:TYPE ADV;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setAvgFilterStatus(ec.UnitMode.CURR, ec.AverFilterType.NONE)
        expectedResult = ":SENS:CURR:AVER:TYPE NONE;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setAvgFilterStatus(ec.UnitMode.CURR, ec.AverFilterType.SCAL)
        expectedResult = ":SENS:CURR:AVER:TYPE SCAL;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setAvgFilterStatus(ec.UnitMode.CHAR, ec.AverFilterType.ADV)
        expectedResult = ":SENS:CHAR:AVER:TYPE ADV;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setAvgFilterStatus(ec.UnitMode.CHAR, ec.AverFilterType.NONE)
        expectedResult = ":SENS:CHAR:AVER:TYPE NONE;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setAvgFilterStatus(ec.UnitMode.CHAR, ec.AverFilterType.SCAL)
        expectedResult = ":SENS:CHAR:AVER:TYPE SCAL;"
        self.assertEqual(command, expectedResult)

    def test_alwaysRead(self):
        command = self.electrometerController.alwaysRead()
        expectedResult = ":TRAC:FEED:CONT ALW;\n:INIT;"
        self.assertEqual(command, expectedResult)

    def test_clearBuffer(self):
        command = self.electrometerController.clearBuffer()
        expectedResult = ":TRAC:CLE;"
        self.assertEqual(command, expectedResult)

    def test_clearDevice(self):
        command = self.electrometerController.clearDevice()
        expectedResult = "^C"
        self.assertEqual(command, expectedResult)

    def test_getLastError(self):
        command = self.electrometerController.getLastError()
        expectedResult = ":SYST:ERR?;"
        self.assertEqual(command, expectedResult)


    def test_formatTrac(self):
        command = self.electrometerController.formatTrac(True, True, True)
        expectedResult = ":TRAC:ELEM CHAN, TST, ETEM;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.formatTrac(True, False, True)
        expectedResult = ":TRAC:ELEM CHAN, ETEM;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.formatTrac(False, False, False)
        expectedResult = ":TRAC:ELEM NONE;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.formatTrac(True, False, False)
        expectedResult = ":TRAC:ELEM CHAN;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.formatTrac(True, True, False)
        expectedResult = ":TRAC:ELEM CHAN, TST;"
        self.assertEqual(command, expectedResult)

    def test_getBufferQuantity(self):
        command = self.electrometerController.getBufferQuantity()
        expectedResult = ":TRAC:POIN:ACT?;"
        self.assertEqual(command, expectedResult)

    def test_getHardwareInfo(self):
        command = self.electrometerController.getHardwareInfo()
        expectedResult = "*IDN?"
        self.assertEqual(command, expectedResult)

    def test_getMeasure(self):
        command = self.electrometerController.getMeasure(ec.readingOption.LATEST)
        expectedResult = ":SENS:DATA?;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.getMeasure(ec.readingOption.NEWREAD)
        expectedResult = ":SENS:DATA:FRES?;"
        self.assertEqual(command, expectedResult)

    def test_getMode(self):
        command = self.electrometerController.getMode()
        expectedResult = ":SENS:FUNC?;"
        self.assertEqual(command, expectedResult)

    def test_enableTemperatureReading(self):
        command = self.electrometerController.enableTemperatureReading(True)
        expectedResult = ":SYST:TSC ON;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.enableTemperatureReading(False)
        expectedResult = ":SYST:TSC OFF;"
        self.assertEqual(command, expectedResult)

    def test_readBuffer(self):
        command = self.electrometerController.readBuffer()
        expectedResult = ":TRAC:DATA?;"
        self.assertEqual(command, expectedResult)

    def test_selectDeviceTimer(self):
        command = self.electrometerController.selectDeviceTimer()
        expectedResult = "TRIG:SOUR TIM;\nTRIG:TIM 0.001;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.selectDeviceTimer(0.1)
        expectedResult = "TRIG:SOUR TIM;\nTRIG:TIM 0.100;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.selectDeviceTimer(0.05)
        expectedResult = "TRIG:SOUR TIM;\nTRIG:TIM 0.050;"
        self.assertEqual(command, expectedResult)

    def test_setBufferSize(self):
        command = self.electrometerController.setBufferSize()
        expectedResult = ":TRACE:CLEAR;\n:TRAC:POINTS 50000;\n:TRIG:COUNT 50000;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setBufferSize(500)
        expectedResult = ":TRACE:CLEAR;\n:TRAC:POINTS 500;\n:TRIG:COUNT 500;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setBufferSize(300)
        expectedResult = ":TRACE:CLEAR;\n:TRAC:POINTS 300;\n:TRIG:COUNT 300;"
        self.assertEqual(command, expectedResult)

    def test_integrationTime(self):
        command = self.electrometerController.integrationTime(ec.UnitMode.CHAR, 0.1)
        expectedResult = ":SENS:CHAR:APER 0.1;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.integrationTime(ec.UnitMode.CHAR, 0.01)
        expectedResult = ":SENS:CHAR:APER 0.01;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.integrationTime(ec.UnitMode.CURR, 0.2)
        expectedResult = ":SENS:CURR:APER 0.2;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.integrationTime(ec.UnitMode.CURR, 0.005)
        expectedResult = ":SENS:CURR:APER 0.005;"
        self.assertEqual(command, expectedResult)

    def test_setMode(self):
        command = self.electrometerController.setMode(ec.UnitMode.CHAR)
        expectedResult = ":SENS:FUNC 'CHAR';"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setMode(ec.UnitMode.CURR)
        expectedResult = ":SENS:FUNC 'CURR';"
        self.assertEqual(command, expectedResult)

    def test_setRange(self):
        command = self.electrometerController.setRange(False, 10, ec.UnitMode.CURR)
        expectedResult = ":SENS:CURR:RANG:AUTO 0;\n:SENS:CURR:RANG 10;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setRange(False, 0.1, ec.UnitMode.CHAR)
        expectedResult = ":SENS:CHAR:RANG:AUTO 0;\n:SENS:CHAR:RANG 0.1;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.setRange(True, 10, ec.UnitMode.CURR)
        expectedResult = ":SENS:CURR:RANG:AUTO 1;\n:SENS:CURR:RANG 10;"
        self.assertEqual(command, expectedResult)

    def test_enableSync(self):
        command = self.electrometerController.enableSync(False)
        expectedResult = ":SYSTEM:LSYN:STAT OFF;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.enableSync(True)
        expectedResult = ":SYSTEM:LSYN:STAT ON;"
        self.assertEqual(command, expectedResult)

    def test_stopReadingBuffer(self):
        command = self.electrometerController.stopReadingBuffer()
        expectedResult = ":TRAC:FEED:CONT NEV;"
        self.assertEqual(command, expectedResult)

    def test_enableAllInstrumentErrors(self):
        command = self.electrometerController.enableAllInstrumentErrors()
        expectedResult = ":STAT:QUE:ENAB (-440:+958);"
        self.assertEqual(command, expectedResult)

    def test_enableZeroCheck(self):
        command = self.electrometerController.enableZeroCheck(True)
        expectedResult = ":SYST:ZCH ON;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.enableZeroCheck(False)
        expectedResult = ":SYST:ZCH OFF;"
        self.assertEqual(command, expectedResult)

    def test_enableZeroCorrection(self):
        command = self.electrometerController.enableZeroCorrection(True)
        expectedResult = ":SYST:ZCOR ON;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.enableZeroCorrection(False)
        expectedResult = ":SYST:ZCOR OFF;"
        self.assertEqual(command, expectedResult)

    def test_getIntegrationTime(self):
        command = self.electrometerController.getIntegrationTime(ec.UnitMode.CURR)
        expectedResult = ":SENS:CURR:APER?;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.getIntegrationTime(ec.UnitMode.CHAR)
        expectedResult = ":SENS:CHAR:APER?;"
        self.assertEqual(command, expectedResult)

    def test_getRange(self):
        command = self.electrometerController.getRange(ec.UnitMode.CHAR)
        expectedResult = ":SENS:CHAR:RANG?;"
        self.assertEqual(command, expectedResult)

        command = self.electrometerController.getRange(ec.UnitMode.CURR)
        expectedResult = ":SENS:CURR:RANG?;"
        self.assertEqual(command, expectedResult)



if __name__ == "__main__":
    unittest.main()