import ElectrometerController

if __name__ == "__main__":
    electrometer = ElectrometerController.ElectrometerController()
    electrometer.updateSerialConfiguration(path="settingFiles", settingsSet="Test", settingsVersion=1)
    electrometer.configureCommunicator()
    errorCode, errorMsg = electrometer.connect()
    print(errorMsg)