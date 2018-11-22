
import QTHelpers
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGridLayout)

class OverviewPageWidget(QWidget):
    def __init__(self, Electrometer):
        QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.layout = QVBoxLayout()
        self.dataLayout = QGridLayout()
        self.layout.addLayout(self.dataLayout)
        self.setLayout(self.layout)
        
        row = 0
        col = 0
        self.summaryStateLabel = QLabel("UNKNOWN")
        self.dataLayout.addWidget(QLabel("Summary State"), row, col)
        self.dataLayout.addWidget(self.summaryStateLabel, row, col + 1)

        self.Electrometer.subscribeEvent_summaryState(self.processEventSummaryState)
        
    def processEventSummaryState(self, data):
        state = data[-1].summaryState
        summaryStates = ["Offline", "Disabled", "Enabled", "Fault", "Offline", "Standby"]
        self.summaryStateLabel.setText(summaryStates[state])