from . import data

hal_data = data.hal_data

from . import functions


class SPISimBase:
    """
        Base class to use for SPI protocol simulators.

        Has all functions that need to be implemented, but throws exceptions
        when data is asked of it. Will throw away set* function data, as most
        low-fidelity simulation will probably not care about such things.
    """

    def initializeSPI(self, port, status):
        self.port = port
        status.value = 0

    def transactionSPI(self, port, dataToSend, dataReceived, size):
        """
            Writes data to the I2C device and then reads from it. You can read
            bytes from the ``dataToSend`` parameter. To return data,
            you need to write bytes to the ``data_received`` parameter.
            object.
            
            A simple example of returning 3 bytes might be::
            
                def transactionSPI(self, port, dataToSend, dataReceived, size):
                    dataReceived[:] = b'123'
                    return len(dataReceived)
            
            :returns: number of bytes returned
        """
        raise NotImplementedError(
            "This error only occurs in simulation if you don't implement a custom interface for your SPI device. See the SPISimBase documentation for details"
        )

    def writeSPI(self, port, dataToSend, sendSize):
        """:returns: number of bytes written"""
        return sendSize

    def readSPI(self, port, buffer, count):
        """
            Reads data from the SPI device. To return data to your code, you
            need to write bytes to the ``buffer`` parameter. A simple example of
            returning 3 bytes might be::
            
                def readSPI(self, port, buffer, count):
                    buffer[:] = b'123'
                    return len(buffer)
            
            :returns: number of bytes read
        """
        raise NotImplementedError(
            "This error only occurs in simulation if you don't implement a custom interface for your SPI device. See the SPISimBase documentation for details"
        )

    def closeSPI(self, port):
        pass

    def setSPISpeed(self, port, speed):
        pass

    def setSPIOpts(self, port, msbFirst, sampleOnTrailing, clkIdleHigh):
        pass

    def setSPIChipSelectActiveHigh(self, port, status):
        pass

    def setSPIChipSelectActiveLow(self, port, status):
        pass

    def getSPIHandle(self, port):
        pass

    def setSPIHandle(self, port, handle):
        pass

    def initSPIAuto(self, port, bufferSize, status):
        status.value = 0

    def freeSPIAuto(self, port, status):
        status.value = 0

    def startSPIAutoRate(self, port, period, status):
        status.value = 0

    def startSPIAutoTrigger(
        self,
        port,
        digitalSourceHandle,
        analogTriggerType,
        triggerRising,
        triggerFalling,
        status,
    ):
        status.value = 0

    def stopSPIAuto(self, port, status):
        status.value = 0

    def setSPIAutoTransmitData(self, port, dataToSend, dataSize, zeroSize, status):
        status.value = 0

    def forceSPIAutoRead(self, port, status):
        status.value = 0

    def readSPIAutoReceivedData(self, port, buffer, numToRead, timeout, status):
        """:returns: number of bytes read"""
        raise NotImplementedError(
            "This error only occurs in simulation if you don't implement a custom interface for your SPI device. See the SPISimBase documentation for details"
        )

    def getSPIAutoDroppedCount(self, port, status):
        """:returns: int32"""
        raise NotImplementedError(
            "This error only occurs in simulation if you don't implement a custom interface for your SPI device. See the SPISimBase documentation for details"
        )


class ADXRS450_Gyro_Sim(SPISimBase):
    """
        This returns the angle of the gyro as the value of::

            hal_data['robot']['adxrs450_spi_%d_angle']

        Where %d is the i2c port number. Angle should be in degrees.
    """

    def __init__(self, gyro):
        self.kDegreePerSecondPerLSB = gyro.kDegreePerSecondPerLSB
        self.kSamplePeriodUs = 1000000 * gyro.kSamplePeriod
        self.lastAngle = 0
        self.lastTimestamp = 0

    def initializeSPI(self, port, status):
        self.angle_key = "adxrs450_spi_%d_angle" % port
        self.rate_key = "adxrs450_spi_%d_rate" % port

    def setSPIAutoTransmitData(self, port, data_to_send, sendSize, zeroSize, status):
        status.value = 0

    def readSPIAutoReceivedData(self, port, buffer, numToRead, timeout, status):
        """:returns: number of bytes read"""
        status.value = 0

        current = hal_data["robot"].get(self.angle_key, 0)

        if numToRead != 0:
            # buffer is 5 integers:
            # - first integer is timestamp
            # - last 4 integers is the offset value byte by byte (big endian)

            offset = current - self.lastAngle
            self.lastAngle = current
            offset /= self.kSamplePeriodUs * self.kDegreePerSecondPerLSB
            offset = int(offset / 1e-6)

            buffer[0] = self.lastTimestamp
            self.lastTimestamp += 1
            if self.lastTimestamp > 0xFFFFFFFF:
                self.lastTimestamp = 0

            buffer[1] = (offset >> 24) & 0xFF
            buffer[2] = (offset >> 16) & 0xFF
            buffer[3] = (offset >> 8) & 0xFF
            buffer[4] = offset & 0xFF

        return 5

    def readSPI(self, port, buffer, count):
        buffer[:] = (0xFF000000 | (0x5200 << 5)).to_bytes(4, "big")
        return count
