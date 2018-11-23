
from pyqtgraph.Qt import QtGui

class ApplicationStatusWidget(QtGui.QWidget):
    def __init__(self, Electrometer):
        QtGui.QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.mainLayout = QtGui.QVBoxLayout()
        self.label = QtGui.QLabel("Application Status")
        self.mainLayout.addWidget(self.label)
        self.gridLayout = QtGui.QGridLayout()
        self.mainLayout.addLayout(self.gridLayout)     
        
        self.gridLayout.addWidget(QtGui.QLabel("Summary State"), 0, 0)
        self.summaryState = QtGui.QLabel("Offline")
        self.gridLayout.addWidget(self.summaryState, 0, 1)
        self.setLayout(self.mainLayout)
        self.detailedStateLabel = QtGui.QLabel("UNKNOWN")
        self.gridLayout.addWidget(QtGui.QLabel("Detailed State"), 1, 0)
        self.gridLayout.addWidget(self.detailedStateLabel, 1, 1)

        self.Electrometer.subscribeEvent_summaryState(self.processEventSummaryState)
        self.Electrometer.subscribeEvent_detailedState(self.processEventDetailedState)

    def processEventSummaryState(self, data):
        state = data[-1].summaryState
        states = ["Offline", "Disabled", "Enabled", "Fault", "Offline", "Standby"]
        self.summaryState.setText(states[state])

    def processEventDetailedState(self, data):
        state = data[-1].detailedState
        deatiledStates = ["Offline", "Disabled", "Enabled", "Fault", "Offline", "Standby","NotReadingState","ConfiguringState","ManualReadingState","ReadingBufferState","SetDurationReadingState"]
        self.detailedStateLabel.setText(deatiledStates[state])