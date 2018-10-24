import unittest
import ConfigurationFileReaderYaml as ryaml

class TestConfigurationReader(unittest.TestCase):

    def setUp(self):
        self.fileYaml = ryaml.FileReaderYaml(".", "Test", 1)
        self.fileYaml.loadFile("example")

    def test_baudrate(self):
        baudrate = self.fileYaml.readValue('baudrate')
        self.assertEqual(57600, baudrate)

    def test_port(self):
        port = self.fileYaml.readValue('port')
        self.assertEqual("/dev/ttyACM1", port)

    def test_parity(self):
        parity = self.fileYaml.readValue('parity')
        self.assertEqual(0, parity)

    def test_stopBits(self):
        stopBits = self.fileYaml.readValue('stopBits')
        self.assertEqual(10, stopBits)

    def test_byteSize(self):
        byteSize = self.fileYaml.readValue('byteSize')
        self.assertEqual(8, byteSize)

    def test_byteToRead(self):
        byteToRead = self.fileYaml.readValue('byteToRead')
        self.assertEqual(1, byteToRead)

    def test_timeout(self):
        timeout = self.fileYaml.readValue('timeout')
        self.assertEqual(3.3, timeout)

    def test_xonxoff(self):
        xonxoff = self.fileYaml.readValue('xonxoff')
        self.assertEqual(0, xonxoff)

    def test_dsrdtr(self):
        dsrdtr = self.fileYaml.readValue('dsrdtr')
        self.assertEqual(0, dsrdtr)

    def test_termChar(self):
        termChar = self.fileYaml.readValue('termChar')
        self.assertEqual("\n", termChar)