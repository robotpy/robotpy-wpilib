from . import data

hal_data = data.hal_data


class SerialSimBase:
    """
        Base class to use for Serial protocol simulators
        
        Has all functions that need to be implemented, but throws exceptions
        when data is asked of it. Will throw away set* function data, as most
        low-fidelity simulation will probably not care about such things. 
    """

    def initializeSerialPort(self, port, status):
        self.port = port
        status.value = 0

    def initializeSerialPortDirect(self, port, portName, status):
        self.port = port
        status.value = 0

    def setSerialBaudRate(self, port, baud, status):
        status.value = 0

    def setSerialDataBits(self, port, bits, status):
        status.value = 0

    def setSerialParity(self, port, parity, status):
        status.value = 0

    def setSerialStopBits(self, port, stopBits, status):
        status.value = 0

    def setSerialWriteMode(self, port, mode, status):
        status.value = 0

    def setSerialFlowControl(self, port, flow, status):
        status.value = 0

    def setSerialTimeout(self, port, timeout, status):
        status.value = 0

    def enableSerialTermination(self, port, terminator, status):
        status.value = 0

    def disableSerialTermination(self, port, status):
        status.value = 0

    def setSerialReadBufferSize(self, port, size, status):
        status.value = 0

    def setSerialWriteBufferSize(self, port, size, status):
        status.value = 0

    def getSerialBytesReceived(self, port, status):
        status.value = 0

    def readSerial(self, port, buffer, count, status):
        raise NotImplementedError

    def writeSerial(self, port, buffer, count, status):
        status.value = 0
        return int(count)

    def flushSerial(self, port, status):
        status.value = 0

    def clearSerial(self, port, status):
        status.value = 0

    def closeSerial(self, port, status):
        status.value = 0
