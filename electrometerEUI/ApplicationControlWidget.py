
import QTHelpers
from SALPY_Electrometer import *
from pyqtgraph.Qt import QtGui

import ElectrometerEnumerations 

class ApplicationControlWidget(QtGui.QWidget):
    def __init__(self, Electrometer):
        QtGui.QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.label = QtGui.QLabel("Application Control")
        self.button1 = QtGui.QPushButton("Button1")
        QTHelpers.updateSizePolicy(self.button1)
        self.button1.clicked.connect(QTHelpers.doNothing)
        self.button2 = QtGui.QPushButton("Button2")
        QTHelpers.updateSizePolicy(self.button2)
        self.button2.clicked.connect(QTHelpers.doNothing)
        self.button3 = QtGui.QPushButton("Button3")
        QTHelpers.updateSizePolicy(self.button3)
        self.button3.clicked.connect(QTHelpers.doNothing)
        self.button4 = QtGui.QPushButton("Button4")
        QTHelpers.updateSizePolicy(self.button4)
        self.button4.clicked.connect(QTHelpers.doNothing)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.button3)
        self.layout.addWidget(self.button4)

        QTHelpers.hideButton(self.button1)
        QTHelpers.hideButton(self.button2)
        QTHelpers.hideButton(self.button3)
        QTHelpers.hideButton(self.button4)

        self.setLayout(self.layout)
        self.Electrometer.subscribeEvent_summaryState(self.processEventSummaryState)

    def issueCommandStart(self):
        self.Electrometer.issueCommand_start("Default1")

    def issueCommandEnable(self):
        self.Electrometer.issueCommand_enable(False)

    def issueCommandDisable(self):
        self.Electrometer.issueCommand_disable(False)

    def issueCommandStandby(self):
        self.Electrometer.issueCommand_standby(False)

    def processEventSummaryState(self, data):
        state = data[-1].summaryState
        if state == SAL__STATE_STANDBY:
            QTHelpers.updateButton(self.button1, "Start", self.issueCommandStart)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.hideButton(self.button4)
        elif state == SAL__STATE_DISABLED:
            QTHelpers.updateButton(self.button1, "Enable", self.issueCommandEnable)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.updateButton(self.button4, "Standby", self.issueCommandStandby)
        elif state == SAL__STATE_ENABLED:
            QTHelpers.hideButton(self.button1)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.updateButton(self.button4, "Disable", self.issueCommandDisable)
        elif state == SAL__STATE_FAULT:
            QTHelpers.hideButton(self.button1)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.updateButton(self.button4, "Standby", self.issueCommandStandby)
        elif state == SAL__STATE_OFFLINE:
            QTHelpers.hideButton(self.button1)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.hideButton(self.button4)

