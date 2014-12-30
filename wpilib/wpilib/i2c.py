#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

__all__ = ["I2C"]

def _freeI2C(port):
    hal.i2CClose(port)

class I2C:
    """I2C bus interface class.

    This class is intended to be used by sensor (and other I2C device) drivers.
    It probably should not be used directly.
    """
    class Port:
        kOnboard = 0
        kMXP = 1

    def __init__(self, port, deviceAddress):
        """Constructor.

        :param port: The I2C port the device is connected to.
        :param deviceAddress: The address of the device on the I2C bus.
        """
        self.port = port
        self.deviceAddress = deviceAddress

        hal.i2CInitialize(self.port)
        self._i2c_finalizer = weakref.finalize(self, _freeI2C, self.port)

        hal.HALReport(hal.HALUsageReporting.kResourceType_I2C, deviceAddress)

    def transaction(self, dataToSend, receiveSize):
        """Generic transaction.

        This is a lower-level interface to the I2C hardware giving you more
        control over each transaction.

        :param dataToSend:
            Data to send as part of the transaction.
        :param receiveSize:
            Number of bytes to read from the device. [0..7]
        :returns: Data received from the device.
        """
        return hal.i2CTransaction(self.port, self.deviceAddress,
                                  dataToSend, receiveSize)

    def addressOnly(self):
        """Attempt to address a device on the I2C bus.

        This allows you to figure out if there is a device on the I2C bus that
        responds to the address specified in the constructor.

        :returns: Transfer Aborted... False for success, True for aborted.
        """
        try:
            self.transaction([], 0)
        except IOError:
            return True
        return False

    def write(self, registerAddress, data):
        """Execute a write transaction with the device.

        Write a single byte to a register on a device and wait until the
        transaction is complete.

        :param registerAddress:
            The address of the register on the device to be written.
        :param data: The byte to write to the register on the device.
        :returns: Transfer Aborted... False for success, True for aborted.
        """
        try:
            hal.i2CWrite(self.port, self.deviceAddress, [registerAddress, data])
        except IOError:
            return True
        return False

    def writeBulk(self, data):
        """Execute a write transaction with the device.

        Write multiple bytes to a register on a device and wait until the
        transaction is complete.

        :param data: The data to write to the device.
        :returns: Transfer Aborted... False for success, True for aborted.
        """
        try:
            hal.i2CWrite(self.port, self.deviceAddress, data)
        except IOError:
            return True
        return False

    def read(self, registerAddress, count):
        """Execute a read transaction with the device.

        Read 1 to 7 bytes from a device. Most I2C devices will auto-increment
        the register pointer internally allowing you to read up to 7
        consecutive registers on a device in a single transaction.

        :param registerAddress: The register to read first in the transaction.
        :param count: The number of bytes to read in the transaction. [1..7]
        :returns: The data read from the device.
        """
        if count < 1 or count > 7:
            raise ValueError("count must be between 1 and 7")
        return self.transaction([registerAddress], count)

    def readOnly(self, count):
        """Execute a read only transaction with the device.

        Read 1 to 7 bytes from a device. This method does not write any data
        to prompt the device.

        :param count: The number of bytes to read in the transaction. [1..7]
        :returns: The data read from the device.
        """
        if count < 1 or count > 7:
            raise ValueError("count must be between 1 and 7")
        hal.i2CRead(self.port, self.deviceAddress, count)

    def broadcast(self, registerAddress, data):
        """Send a broadcast write to all devices on the I2C bus.

        .. warning:: This is not currently implemented!

        :param registerAddress:
            The register to write on all devices on the bus.
        :param data: The value to write to the devices.
        """
        raise NotImplementedError

    def verifySensor(self, registerAddress, expected):
        """Verify that a device's registers contain expected values.

        Most devices will have a set of registers that contain a known value
        that can be used to identify them. This allows an I2C device driver
        to easily verify that the device contains the expected value.

        The device must support and be configured to use register
        auto-increment.

        :param registerAddress:
            The base register to start reading from the device.
        :param expected: The values expected from the device.
        :returns: True if the sensor was verified to be connected
        """
        # TODO: Make use of all 7 read bytes
        count = len(expected)
        for i in range(0, count, 4):
            toRead = 4
            if (count - i) < 4:
                toRead = count - i
            # Read the chunk of data. Return False if the sensor does not
            # respond.
            try:
                deviceData = self.read(registerAddress, toRead)
            except IOError:
                return False

            for j in range(toRead):
                if deviceData[j] != expected[i + j]:
                    return False

            registerAddress += count

        return True
