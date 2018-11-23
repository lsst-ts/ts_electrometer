
import QTHelpers
from SALPY_Electrometer import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

import numpy as np

import ElectrometerEnumerations 

class ElectrometerPlotWidget(QtGui.QWidget):
    def __init__(self, Electrometer):
        QtGui.QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.layout = QtGui.QVBoxLayout()
        self.dataLayout = QtGui.QGridLayout()

        self.maxPlotSize = 50 * 30 # 50Hz * 30s

        self.label = QtGui.QLabel("Light Intensity Plot")
        self.layout.addWidget(self.label)

        self.plot = pg.PlotWidget(name='Light intensity')
        self.plot.plotItem.addLegend()
        self.plot.plotItem.setTitle("Light Intensity")
        self.plot.plotItem.setLabel(axis = 'left', text = "Intensity")
        self.plot.plotItem.setLabel(axis = 'bottom', text = "Time (s)")
        self.layout.addLayout(self.dataLayout)
        self.layout.addWidget(self.plot)
        self.setLayout(self.layout)
        self.intensity = np.array([np.zeros(0)])
        self.intensityPlot = self.plot.plot(name = 'Intensity', pen = 'r')
        
        #self.angularVelocityYCurve = self.plot.plot(name = 'Y', pen = 'g')
        #self.angularVelocityYCurveData = np.array([np.zeros(self.maxPlotSize)])

        self.Electrometer.subscribeEvent_intensity(self.processEventsIntensity)

    def processEventsIntensity(self, data):
        self.intensity = QTHelpers.appendAndResizeCurveData(self.intensity, [x.intensity for x in data], self.maxPlotSize)
        self.intensityPlot.setData(self.intensity)
        """
        data = data[-1]
        self.velocityXLabel.setText("%0.3f" % (data.angularVelocityX))
        self.velocityYLabel.setText("%0.3f" % (data.angularVelocityY))
        self.velocityZLabel.setText("%0.3f" % (data.angularVelocityZ))
        self.sequenceNumberLabel.setText("%0.3f" % (data.sequenceNumber))
        self.temperatureLabel.setText("%0.3f" % (data.temperature))
        """