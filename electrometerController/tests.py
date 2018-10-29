
if __name__ == "__main__":
    electrometer = ElectrometerController()
    electrometer.configureCommunicator(port="/dev/electrometer", baudrate=57600, parity='N', stopbits=1, bytesize=8, byteToRead=1024, dsrdtr=0, xonxoff=0, timeout=0.01, termChar="\n")
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

    if(False): #Read during t time
        loop = asyncio.get_event_loop()
        values, times = loop.run_until_complete(electrometer.readDuringTime(4))
        print(values)
        print(times)

    if(True): #update parameters
        print("mode1:"+str(electrometer.setMode(ec.UnitMode.CURR)))
        print("IntTime1:"+str(electrometer.setIntegrationTime(0.01)))
        print("Range1:"+str(electrometer.setRange(0.05)))

        mode = electrometer.getMode()
        print("IntTime2:"+mode.name)
        intTime = electrometer.getIntegrationTime()
        print("IntTime2:"+str(intTime))
        rangeValue = electrometer.getRange()
        print("range2:"+str(rangeValue))
        
        
        
    electrometer.updateState(iec.ElectrometerStates.NOTREADINGSTATE)
    errorCodes, errorMessages = electrometer.getErrorList()
    #print( str(errorCodes)+str(errorMessages) )
    electrometer.disconnect()

