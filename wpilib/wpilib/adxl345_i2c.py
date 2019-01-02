# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/ADXL345_I2C.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import enum

from typing import Tuple, Optional

import hal
from .i2c import I2C
from .sendablebase import SendableBase
from .interfaces import Accelerometer
from .sendablebuilder import SendableBuilder

__all__ = ["ADXL345_I2C"]


class ADXL345_I2C(SendableBase):
    """
        ADXL345 accelerometer device via i2c
    """

    kAddress = 0x1D
    kPowerCtlRegister = 0x2D
    kDataFormatRegister = 0x31
    kDataRegister = 0x32
    kGsPerLSB = 0.00390625

    kPowerCtl_Link = 0x20
    kPowerCtl_AutoSleep = 0x10
    kPowerCtl_Measure = 0x08
    kPowerCtl_Sleep = 0x04

    kDataFormat_SelfTest = 0x80
    kDataFormat_SPI = 0x40
    kDataFormat_IntInvert = 0x20
    kDataFormat_FullRes = 0x08
    kDataFormat_Justify = 0x04

    Range = Accelerometer.Range

    class Axes(enum.IntEnum):
        kX = 0x00
        kY = 0x02
        kZ = 0x04

    def __init__(
        self, port: I2C.Port, range: Range, address: Optional[int] = None
    ) -> None:
        """Constructor.

        :param port: The I2C port the accelerometer is attached to.
        :param range: The range (+ or -) that the accelerometer will measure.
        :param address: the I2C address of the accelerometer (0x1D or 0x53)
        """
        if address is None:
            address = self.kAddress

        self.i2c = I2C(port, address)

        # Turn on the measurements
        self.i2c.write(self.kPowerCtlRegister, self.kPowerCtl_Measure)

        self.setRange(range)

        hal.report(
            hal.UsageReporting.kResourceType_ADXL345, hal.UsageReporting.kADXL345_I2C
        )

        self.setName("ADXL345_I2C", port)

    def close(self) -> None:
        self.i2c.close()
        super().close()

    # Accelerometer interface

    def setRange(self, range: Range) -> None:
        """Set the measuring range of the accelerometer.

        :param range: The maximum acceleration, positive or negative, that
                      the accelerometer will measure.
        """
        if range == self.Range.k2G:
            value = 0
        elif range == self.Range.k4G:
            value = 1
        elif range == self.Range.k8G:
            value = 2
        elif range == self.Range.k16G:
            value = 3
        else:
            raise ValueError("Invalid range argument '%s'" % range)

        # Specify the data format to read
        self.i2c.write(self.kDataFormatRegister, self.kDataFormat_FullRes | value)

    def getX(self) -> float:
        """Get the x axis acceleration

        :returns: The acceleration along the x axis in g-forces
        """
        return self.getAcceleration(self.Axes.kX)

    def getY(self) -> float:
        """Get the y axis acceleration

        :returns: The acceleration along the y axis in g-forces
        """
        return self.getAcceleration(self.Axes.kY)

    def getZ(self) -> float:
        """Get the z axis acceleration

        :returns: The acceleration along the z axis in g-forces
        """
        return self.getAcceleration(self.Axes.kZ)

    def getAcceleration(self, axis: Axes) -> float:
        """Get the acceleration of one axis in Gs.

        :param axis: The axis to read from.
        :returns: An object containing the acceleration measured on each axis of the ADXL345 in Gs.
        """
        data = self.i2c.read(self.kDataRegister + axis, 2)
        # Sensor is little endian... swap bytes
        rawAccel = (data[1] << 8) | data[0]
        return rawAccel * self.kGsPerLSB

    def getAccelerations(self) -> Tuple[float, float, float]:
        """Get the acceleration of all axes in Gs.

        :returns: X,Y,Z tuple of acceleration measured on all axes of the
                  ADXL345 in Gs.
        """
        data = self.i2c.read(self.kDataRegister, 6)

        # Sensor is little endian... swap bytes
        rawData = []
        for i in range(3):
            rawData.append((data[i * 2 + 1] << 8) | data[i * 2])

        return (
            rawData[0] * self.kGsPerLSB,
            rawData[1] * self.kGsPerLSB,
            rawData[2] * self.kGsPerLSB,
        )

    def _updateValues(self) -> None:
        data = self.getAccelerations()
        self._entryX.setDouble(data[0])
        self._entryY.setDouble(data[1])
        self._entryZ.setDouble(data[2])

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("3AxisAccelerometer")
        self._entryX = builder.getEntry("X")
        self._entryY = builder.getEntry("Y")
        self._entryZ = builder.getEntry("Z")

        builder.setUpdateTable(self._updateValues)
