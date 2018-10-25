from pythonCommunicator.TcpCommunicator import TcpClient, TcpClienEndChar

# testClass = TcpClient(address="192.168.0.1", port=5000)
# a, b = testClass.connect()
# testClass.disconnect()

testClass2 = TcpClienEndChar(address="localhost", port=5000)
a, b = testClass2.connect()
error1, errorMsg1 = testClass2.sendMessage("Client: How you doing...\n")
error2, message, errorMsg2 = testClass2.getMessage()

print(str(b))
#print(repr(errorMsg1))
#print(repr(errorMsg2))
#testClass2.disconnect()

#print(b)
print("Program ended")