#!/usr/bin/python3
# -'''- coding: utf-8 -'''-

import sys
import time

from ElectrometerRemote import ElectrometerRemote

from ApplicationControlWidget import ApplicationControlWidget
from ApplicationStatusWidget import ApplicationStatusWidget
from ApplicationPaginationWidget import ApplicationPaginationWidget

from OverviewPageWidget import OverviewPageWidget

from ElectrometerControlsWidget import ElectrometerControlsWidget
from ElectrometerPlot import ElectrometerPlotWidget

from pyqtgraph.Qt import QtGui
from PyQt5.QtCore import QTimer, QDateTime

class EUI(QtGui.QDialog):
    def __init__(self, Electrometer, parent=None):
        super(EUI, self).__init__(parent)
        self.Electrometer = Electrometer
        self.layout = QtGui.QVBoxLayout()
        self.topLayerLayout = QtGui.QHBoxLayout()
        self.applicationControl = ApplicationControlWidget(Electrometer)
        self.topLayerLayout.addWidget(self.applicationControl)
        self.applicationStatus = ApplicationStatusWidget(Electrometer)
        self.topLayerLayout.addWidget(self.applicationStatus)
        self.middleLayerLayout = QtGui.QHBoxLayout()
        self.applicationPagination = ApplicationPaginationWidget(Electrometer)

        self.applicationPagination.addPage("Overview", OverviewPageWidget(Electrometer))
        self.applicationPagination.addPage("Controls", ElectrometerControlsWidget(Electrometer))
        self.applicationPagination.addPage("Plot", ElectrometerPlotWidget(Electrometer))

        self.middleLayerLayout.addWidget(self.applicationPagination)
        self.bottomLayerLayout = QtGui.QHBoxLayout()
        self.layout.addLayout(self.topLayerLayout)
        self.layout.addLayout(self.middleLayerLayout)
        self.layout.addLayout(self.bottomLayerLayout)
        self.setLayout(self.layout)

if __name__ == '__main__':
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create EUI
    Electrometer = ElectrometerRemote()
    eui = EUI(Electrometer)
    eui.show()
    # Create Electrometer Telemetry & Event Loop
    telemetryEventLoopTimer = QTimer()
    telemetryEventLoopTimer.timeout.connect(Electrometer.runSubscriberChecks)
    telemetryEventLoopTimer.start(500)
    # Run the main Qt loop
    app.exec_()
    # Clean up Electrometer Telemetry & Event Loop
    telemetryEventLoopTimer.stop()
    # Close application
    sys.exit()