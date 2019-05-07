
import QTHelpers
from ElectrometerEnumerations import UnitToRead
from pyqtgraph.Qt import QtGui

class ElectrometerControlsWidget(QtGui.QWidget):
    def __init__(self, Electrometer):
        QtGui.QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.layout = QtGui.QGridLayout()
        self.controlsLayout = QtGui.QGridLayout()
        self.dataLayout = QtGui.QGridLayout()

        self.layout.addLayout(self.controlsLayout, 0, 0)
        self.layout.addLayout(self.dataLayout, 1, 0)

        #Controls
        self.manualScan = QtGui.QPushButton("ManualScan")
        QTHelpers.updateSizePolicy(self.manualScan)
        self.manualScan.clicked.connect(self.issueCommandManualScan)

        self.timeScan = QtGui.QPushButton("TimeScan")
        QTHelpers.updateSizePolicy(self.timeScan)
        self.timeScan.clicked.connect(self.issueCommandTimeScan)

        self.setDigitalFilter = QtGui.QPushButton("SetDigitalFilter")
        QTHelpers.updateSizePolicy(self.setDigitalFilter)
        self.setDigitalFilter.clicked.connect(self.issueCommandSetDigitalFilter)

        self.setIntegrationTime = QtGui.QPushButton("SetIntegrationTime")
        QTHelpers.updateSizePolicy(self.setIntegrationTime)
        self.setIntegrationTime.clicked.connect(self.issueCommandSetIntegrationTime)

        self.setMeasureType = QtGui.QPushButton("SetMeasureType")
        QTHelpers.updateSizePolicy(self.setMeasureType)
        self.setMeasureType.clicked.connect(self.issueCommandSetMeasureType)

        self.setMasureRange = QtGui.QPushButton("SetMeasureRange")
        QTHelpers.updateSizePolicy(self.setMasureRange)
        self.setMasureRange.clicked.connect(self.issueCommandSetMasureRange)

        self.performZeroCalibration = QtGui.QPushButton("PerformZeroCalibration")
        QTHelpers.updateSizePolicy(self.performZeroCalibration)
        self.performZeroCalibration.clicked.connect(self.issueCommandPerformZeroCalibration)

        self.stopScan = QtGui.QPushButton("StopScan")
        QTHelpers.updateSizePolicy(self.stopScan)
        self.stopScan.clicked.connect(self.issueCommandStopScan)


        row = 0
        col = 0
        self.label = QtGui.QLabel("Electrometer Controls")
        self.controlsLayout.addWidget(self.label)
        self.controlsLayout.addWidget(self.manualScan, row, col)
        self.controlsLayout.addWidget(self.timeScan, row+1, col)
        self.controlsLayout.addWidget(self.setDigitalFilter, row+2, col)
        self.controlsLayout.addWidget(self.setIntegrationTime, row+3, col)
        self.controlsLayout.addWidget(self.setMeasureType, row+4, col)
        self.controlsLayout.addWidget(self.setMasureRange, row+5, col)
        self.controlsLayout.addWidget(self.performZeroCalibration, row+6, col)
        self.controlsLayout.addWidget(self.stopScan, row+7, col)

        self.digitalFilterInput = QtGui.QLineEdit()
        self.digitalFilterInput.setValidator(QtGui.QIntValidator(0, 1))
        self.digitalFilterInput.setText("1")

        self.scanTimeInput = QtGui.QLineEdit()
        self.scanTimeInput.setValidator(QtGui.QDoubleValidator(0, 60, 3))
        self.scanTimeInput.setText("5")

        self.integrationTimeInput = QtGui.QLineEdit()
        self.integrationTimeInput.setValidator(QtGui.QDoubleValidator(0, 100, 3))
        self.integrationTimeInput.setText("0")

        self.measureTypeInput = QtGui.QLineEdit()
        self.measureTypeInput.setValidator(QtGui.QIntValidator(1, 2))
        self.measureTypeInput.setText("1")

        self.mesureRangeInput = QtGui.QLineEdit()
        self.mesureRangeInput.setValidator(QtGui.QDoubleValidator(-100, 100, 3))
        self.mesureRangeInput.setText("0")
        
        col+=1
        self.controlsLayout.addWidget(self.scanTimeInput, row+1, col)
        self.controlsLayout.addWidget(self.digitalFilterInput, row+2, col)
        self.controlsLayout.addWidget(self.integrationTimeInput, row+3, col)
        self.controlsLayout.addWidget(self.measureTypeInput, row+4, col)
        self.controlsLayout.addWidget(self.mesureRangeInput, row+5, col)

        row = 0
        col = 0

        #Data
        self.digitalFilterLabel = QtGui.QLabel("UNKNOWN")
        self.integrationTimeLabel = QtGui.QLabel("UNKNOWN")
        self.intensityLabel = QtGui.QLabel("UNKNOWN")
        self.measureRangeLabel = QtGui.QLabel("UNKNOWN")
        self.measureTypeLabel = QtGui.QLabel("UNKNOWN")
        
        self.dataLayout.addWidget(QtGui.QLabel("Digital Filter"), row, col + 0)
        self.dataLayout.addWidget(QtGui.QLabel("Integration Time"), row, col + 1)
        self.dataLayout.addWidget(QtGui.QLabel("Intensity"), row, col + 2)
        self.dataLayout.addWidget(QtGui.QLabel("Range"), row, col + 3)
        self.dataLayout.addWidget(QtGui.QLabel("Measuring Mode"), row, col + 4)
        row += 1
        
        self.dataLayout.addWidget(self.digitalFilterLabel, row, col + 0)
        self.dataLayout.addWidget(self.integrationTimeLabel, row, col + 1)
        self.dataLayout.addWidget(self.intensityLabel, row, col + 2)
        self.dataLayout.addWidget(self.measureRangeLabel, row, col + 3)
        self.dataLayout.addWidget(self.measureTypeLabel, row, col + 4)

        self.setLayout(self.layout)
        
        self.Electrometer.subscribeEvent_detailedState(self.processEventDetailedState)
        self.Electrometer.subscribeEvent_digitalFilterChange(self.processEventDigitalFilterChange)
        self.Electrometer.subscribeEvent_integrationTime(self.processEventIntegrationTime)
        self.Electrometer.subscribeEvent_intensity(self.processEventIntensity)
        self.Electrometer.subscribeEvent_measureRange(self.processEventMeasureRange)
        self.Electrometer.subscribeEvent_measureType(self.processEventMeasureType)        
        
    def processEventDetailedState(self, data):
        state = data[-1].detailedState

    def processEventDigitalFilterChange(self, data):
        activateMedianFilter = data[-1].activateMedianFilter
        activateAverageFilter = data[-1].activateAverageFilter
        activateFilter = data[-1].activateFilter
        filter = "Active" if bool(activateFilter) else "Not Active"

        self.digitalFilterLabel.setText(filter)

    def processEventIntegrationTime(self, data):
        integrationTime = data[-1].intTime
        self.integrationTimeLabel.setText("%0.3f" % integrationTime)

    def processEventIntensity(self, data):
        intensity = data[-1].intensity
        unit = data[-1].unit
        timestamp = data[-1].timestamp
        self.intensityLabel.setText("%0.3f" % intensity)

    def processEventMeasureRange(self, data):
        rangeValue = data[-1].rangeValue
        self.measureRangeLabel.setText("%0.3f" % rangeValue)

    def processEventMeasureType(self, data):
        mode = data[-1].mode
        self.measureTypeLabel.setText("%0.3f" % mode)

    def issueCommandManualScan(self):
        self.Electrometer.issueCommand_startScan(True)

    def issueCommandTimeScan(self):
        scanTimeInput = float(self.scanTimeInput.text())
        self.Electrometer.issueCommand_startScanDt(scanTimeInput)

    def issueCommandSetDigitalFilter(self):  
        active = bool(int(self.digitalFilterInput.text()))
        self.Electrometer.issueCommand_setDigitalFilter(active, active, active)

    def issueCommandSetIntegrationTime(self):
        integrationTime = float(self.integrationTimeInput.text())
        self.Electrometer.issueCommand_setIntegrationTime(integrationTime)

    def issueCommandSetMeasureType(self):
        measureTypeInput = int(self.measureTypeInput.text())
        self.Electrometer.issueCommand_setMode(measureTypeInput)

    def issueCommandSetMasureRange(self):   
        mesureRangeInput = float(self.mesureRangeInput.text())
        self.Electrometer.issueCommand_setRange(mesureRangeInput)

    def issueCommandPerformZeroCalibration(self):   
        self.Electrometer.issueCommand_performZeroCalib(True)        

    def issueCommandStopScan(self):   
        self.Electrometer.issueCommand_stopScan(True)        


