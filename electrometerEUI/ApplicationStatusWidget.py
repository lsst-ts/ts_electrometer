
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout)

class ApplicationStatusWidget(QWidget):
    def __init__(self, Electrometer):
        QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.mainLayout = QVBoxLayout()
        self.label = QLabel("Application Status")
        self.mainLayout.addWidget(self.label)
        self.gridLayout = QGridLayout()
        self.mainLayout.addLayout(self.gridLayout)     
        self.gridLayout.addWidget(QLabel("Summary State"), 0, 0)
        self.summaryState = QLabel("Offline")
        self.gridLayout.addWidget(self.summaryState, 0, 1)
        self.setLayout(self.mainLayout)
        self.detailedStateLabel = QLabel("UNKNOWN")
        self.gridLayout.addWidget(QLabel("Detailed State"), 1, 0)
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