
import QTHelpers
from pyqtgraph.Qt import QtGui

class OverviewPageWidget(QtGui.QWidget):
    def __init__(self, Electrometer):
        QtGui.QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.layout = QtGui.QVBoxLayout()
        self.dataLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.dataLayout)
        self.setLayout(self.layout)
        
        row = 0
        col = 0
        self.summaryStateLabel = QtGui.QLabel("UNKNOWN")
        self.dataLayout.addWidget(QtGui.QLabel("Summary State"), row, col)
        self.dataLayout.addWidget(self.summaryStateLabel, row, col + 1)

        self.Electrometer.subscribeEvent_summaryState(self.processEventSummaryState)
        
    def processEventSummaryState(self, data):
        state = data[-1].summaryState
        summaryStates = ["Offline", "Disabled", "Enabled", "Fault", "Offline", "Standby"]
        self.summaryStateLabel.setText(summaryStates[state])