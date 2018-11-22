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

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import (QApplication, QVBoxLayout, QDialog, QHBoxLayout)

class EUI(QDialog):
    def __init__(self, Electrometer, parent=None):
        super(EUI, self).__init__(parent)
        self.Electrometer = Electrometer
        self.layout = QVBoxLayout()
        self.topLayerLayout = QHBoxLayout()
        self.applicationControl = ApplicationControlWidget(Electrometer)
        self.topLayerLayout.addWidget(self.applicationControl)
        self.applicationStatus = ApplicationStatusWidget(Electrometer)
        self.topLayerLayout.addWidget(self.applicationStatus)
        self.middleLayerLayout = QHBoxLayout()
        self.applicationPagination = ApplicationPaginationWidget(Electrometer)

        self.applicationPagination.addPage("Overview", OverviewPageWidget(Electrometer))
        self.applicationPagination.addPage("Controls", ElectrometerControlsWidget(Electrometer))

        self.middleLayerLayout.addWidget(self.applicationPagination)
        self.bottomLayerLayout = QHBoxLayout()
        self.layout.addLayout(self.topLayerLayout)
        self.layout.addLayout(self.middleLayerLayout)
        self.layout.addLayout(self.bottomLayerLayout)
        self.setLayout(self.layout)

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
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