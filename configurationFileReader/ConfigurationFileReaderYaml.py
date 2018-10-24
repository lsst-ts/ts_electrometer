import ConfigurationFileReader as cfr
import yaml

class FileReaderYaml(cfr.FileReader):

    def __init__(self, path, settingsSet, settingsVersion):
        self.path = path
        self.settingsSet = settingsSet
        self.settingsVersion = str(settingsVersion)
        self.yamlfile = None
        self.separator = "\\"

    def getPath(self, settings):
        return self.path+self.separator+self.settingsSet+self.separator+self.settingsVersion+self.separator+settings+".yaml"

    def getAllAttributes(self):
        return self.yamlfile.keys()

    def readValue(self, attribute):
        return self.yamlfile[attribute]

    def loadFile(self, settings):
        fileReader = FileReaderYaml(self.path, self.settingsSet, self.settingsVersion)
        yamldata = open(fileReader.getPath(settings), "r")
        self.yamlfile = yaml.safe_load(yamldata)
        yamldata.close()

    def setSettingsSet(self, settingsSet, settingsVersion):
        self.settingsSet = settingsSet
        self.settingsVersion = str(settingsVersion)


if __name__ == "__main__":
    fileYaml = FileReaderYaml("..\\settingFiles", "Test", 1)
    fileYaml.loadFile("example")
    print(fileYaml.readStringValue('baudrate'))
    print(fileYaml.getAllAttributes())
