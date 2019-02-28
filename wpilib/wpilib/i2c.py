# validated: 2018-09-09 EN 0e9172f9a708 edu/wpi/first/wpilibj/I2C.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import enum
from typing import List, Union

import hal
import warnings
import weakref

__all__ = ["I2C"]


def _freeI2C(port: "I2C.Port") -> None:
    hal.closeI2C(port)


class I2C:
    """I2C bus interface class.

    This class is intended to be used by sensor (and other I2C device) drivers.
    It probably should not be used directly.
    
    Example usage::
    
        i2c = wpilib.I2C(wpilib.I2C.Port.kOnboard, 4)
        
        # Write bytes 'text', and receive 4 bytes in data
        data = i2c.transaction(b'text', 4)
    """

    class Port(enum.IntEnum):
        kOnboard = 0
        kMXP = 1

    def __init__(self, port: Port, deviceAddress: int, simPort=None) -> None:
        """Constructor.

        :param port: The I2C port the device is connected to.
        :param deviceAddress: The address of the device on the I2C bus.
        :param simPort: This must be an object that implements all of
                        the i2c* functions from hal_impl that you use.
                        See ``test_i2c.py`` for an example.
        """
        if port not in [self.Port.kOnboard, self.Port.kMXP]:
            raise ValueError("Invalid value '%s' for I2C port" % port)

        if hal.HALIsSimulation():
            if simPort is None:
                # If you want more functionality, implement your own mock
                from hal_impl.i2c_helpers import I2CSimBase

                simPort = I2CSimBase()

                msg = "Using stub simulator for I2C port %s" % port
                warnings.warn(msg)

            # Just check for basic functionality
            assert hasattr(simPort, "initializeI2C")
            assert hasattr(simPort, "closeI2C")

            self.port = (simPort, port)
        else:
            self.port = port

        self.deviceAddress = deviceAddress

        hal.initializeI2C(self.port)
        self.__finalizer = weakref.finalize(self, _freeI2C, self.port)

        hal.report(hal.UsageReporting.kResourceType_I2C, deviceAddress)

    def free(self) -> None:
        """
        .. deprecated:: 2019.0.0
            Use close instead
        """
        warnings.warn("use close instead", DeprecationWarning, stacklevel=2)
        self.close()

    def close(self) -> None:
        self.__finalizer()
        self.port = None

    def transaction(
        self, dataToSend: Union[bytes, List[int]], receiveSize: int
    ) -> bytes:
        """Generic transaction.

        This is a lower-level interface to the I2C hardware giving you more
        control over each transaction. If you intend to write multiple bytes
        in the same transaction and do not plan to receive anything back, use
        writeBulk() instead. Calling this with a receiveSize of 0 will
        result in an error.

        :param dataToSend: Buffer of data to send as part of the transaction.
        :param receiveSize: Number of bytes to read from the device.
        :returns: Data received from the device.
        """
        return hal.transactionI2C(
            self.port, self.deviceAddress, dataToSend, receiveSize
        )

    def addressOnly(self) -> bool:
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

    def write(self, registerAddress: int, data: int) -> bool:
        """Execute a write transaction with the device.

        Write a single byte to a register on a device and wait until the
        transaction is complete.

        :param registerAddress:
            The address of the register on the device to be written.
        :param data: The byte to write to the register on the device.
        :returns: Transfer Aborted... False for success, True for aborted.
        """
        try:
            hal.writeI2C(self.port, self.deviceAddress, [registerAddress, data])
        except IOError:
            return True
        return False

    def writeBulk(self, data: bytes) -> bool:
        """Execute a write transaction with the device.

        Write multiple bytes to a register on a device and wait until the
        transaction is complete.

        :param data: The data to write to the device.
        :returns: Transfer Aborted... False for success, True for aborted.
        
        Usage::
        
            # send byte string
            failed = i2c.writeBulk(b'stuff')
            
            # send list of integers
            failed = i2c.write([0x01, 0x02])
        """
        try:
            hal.writeI2C(self.port, self.deviceAddress, data)
        except IOError:
            return True
        return False

    def read(self, registerAddress: int, count: int) -> bytearray:
        """Execute a read transaction with the device.

        Read bytes from a device. Most I2C devices will auto-increment
        the register pointer internally allowing you to read
        consecutive registers on a device in a single transaction.

        :param registerAddress: The register to read first in the transaction.
        :param count: The number of bytes to read in the transaction.
        :returns: The data read from the device.
        """
        if count < 1:
            raise ValueError("count must be at least 1, %s given" % count)
        return self.transaction([registerAddress], count)

    def readOnly(self, count: int) -> bytes:
        """Execute a read only transaction with the device.

        Read bytes from a device. This method does not write any data
        to prompt the device.

        :param count: The number of bytes to read in the transaction.
        :returns: The data read from the device.
        """
        if count < 1:
            raise ValueError("count must be at least 1, %s given" % count)
        return hal.readI2C(self.port, self.deviceAddress, count)

    def verifySensor(self, registerAddress: int, expected: bytes) -> bool:
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
