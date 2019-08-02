import electrometerController.ElectrometerCommands as ec
from pythonCommunicator.SerialCommunicator import SerialCommunicator
from pythonFileReader.ConfigurationFileReaderYaml import FileReaderYaml
import electrometerController.IElectrometerController as iec
from electrometerController.ElectrometerController import ElectrometerController
from time import time
import time as timeFL
from asyncio import sleep
import asyncio
import re
import serial

if __name__ == "__main__":
    electrometer = ElectrometerController()
    electrometer.configureCommunicator(port="/dev/electrometer", baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, byteToRead=128, dsrdtr=0, xonxoff=0, timeout=1, termChar="\n")
    electrometer.connect()

    #response = electrometer.getHardwareInfo()
    electrometer.updateState(iec.ElectrometerStates.NOTREADINGSTATE)
    #electrometer.performZeroCorrection()
    
    electrometer.reset()
    
    print(electrometer.isConnected())

    if(False): #Read buffer test
        electrometer.readManual()
        timetSleep.sleep(4)
        quant = electrometer.getBufferQuantity()
        print(quant)
        loop = asyncio.get_event_loop()
        values, times = loop.run_until_complete(electrometer.stopReading())
        print(values)

    if(True): #Read during t time
        loop = asyncio.get_event_loop()
        values, times = loop.run_until_complete(electrometer.readDuringTime(4))
        print(values)
        print(times)


    if(False): #update parameters
        delay = 0.00
        timeFL.sleep(delay)
        print("mode1:"+str(electrometer.setMode(ec.UnitMode.CURR)))

        timeFL.sleep(delay)
        print("IntTime1:"+str(electrometer.setIntegrationTime(0.01)))
        timeFL.sleep(delay)
        print("Range1:"+str(electrometer.setRange(0.05)))

        timeFL.sleep(delay)
        mode = electrometer.getMode()
        print("IntTime2:"+mode.name)

        timeFL.sleep(delay)
        intTime = electrometer.getIntegrationTime()
        print("IntTime2:"+str(intTime))

        timeFL.sleep(delay)
        rangeValue = electrometer.getRange()
        print("range2:"+str(rangeValue))

        
    if(False): #test filters
        print("activateFilter:"+str(electrometer.activateFilter(False)))
        #print("activateAverageFilter:"+str(electrometer.activateAverageFilter(False)))
        #print("activateMedianFilter:"+str(electrometer.activateMedianFilter(False)))

        getMedianFilterStatusValue = electrometer.getMedianFilterStatus()
        print("getMedianFilterStatusValue2:"+str(getMedianFilterStatusValue))
        getFilterStatusValue = electrometer.getFilterStatus()
        print("getFilterStatusValue2:"+str(getFilterStatusValue))
        getAverageFilterStatusValue = electrometer.getAverageFilterStatus()
        print("getAverageFilterStatusValue2:"+str(getAverageFilterStatusValue))  
        
    electrometer.updateState(iec.ElectrometerStates.NOTREADINGSTATE)
    errorCodes, errorMessages = electrometer.getErrorList()
    #print( str(errorCodes)+str(errorMessages) )
    electrometer.disconnect()


