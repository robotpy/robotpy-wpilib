# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/ADXL362.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import enum
from typing import Tuple, Optional

import hal

from .driverstation import DriverStation
from .interfaces import Accelerometer
from .spi import SPI
from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder

__all__ = ["ADXL362"]


class ADXL362(SendableBase):
    """
        ADXL362 SPI Accelerometer.
    
        This class allows access to an Analog Devices ADXL362 3-axis accelerometer.
        
        .. not_implemented: init
    """

    kRegWrite = 0x0A
    kRegRead = 0x0B

    kPartIdRegister = 0x02
    kDataRegister = 0x0E
    kFilterCtlRegister = 0x2C
    kPowerCtlRegister = 0x2D

    kFilterCtl_Range2G = 0x00
    kFilterCtl_Range4G = 0x40
    kFilterCtl_Range8G = 0x80
    kFilterCtl_ODR_100Hz = 0x03

    kPowerCtl_UltraLowNoise = 0x20
    kPowerCtl_AutoSleep = 0x04
    kPowerCtl_Measure = 0x02

    Range = Accelerometer.Range

    class Axes(enum.IntEnum):
        kX = 0x00
        kY = 0x02
        kZ = 0x04

    def __init__(self, range: Range, port: Optional[SPI.Port] = None) -> None:
        """Constructor.
        
        :param range: The range (+ or -) that the accelerometer will measure.
        :param port: The SPI port that the accelerometer is connected to
        """
        if port is None:
            port = SPI.Port.kOnboardCS1

        self.spi = SPI(port)
        self.spi.setClockRate(3000000)
        self.spi.setMSBFirst()
        self.spi.setSampleDataOnTrailingEdge()
        self.spi.setClockActiveLow()
        self.spi.setChipSelectActiveLow()

        # Validate the part ID
        data = [self.kRegRead, self.kPartIdRegister, 0]
        data = self.spi.transaction(data)
        if data[2] != 0xF2:
            DriverStation.reportError(
                "could not find ADXL362 on SPI port " + port, False
            )
            self.spi.close()
            self.spi = None
            return

        self.setRange(range)

        # Turn on the measurements
        self.spi.write(
            [
                self.kRegWrite,
                self.kPowerCtlRegister,
                self.kPowerCtl_Measure | self.kPowerCtl_UltraLowNoise,
            ]
        )

        hal.report(hal.UsageReporting.kResourceType_ADXL362, port)

        self.setName("ADXL362", port)

    def close(self) -> None:
        if self.spi:
            self.spi.close()
            self.spi = None
        super().close()

    # Accelerometer interface

    def setRange(self, range: Range) -> None:
        """Set the measuring range of the accelerometer.

        :param range: The maximum acceleration, positive or negative, that
                      the accelerometer will measure.
        """
        if not self.spi:
            return

        if range == self.Range.k2G:
            value = self.kFilterCtl_Range2G
            self.gsPerLSB = 0.001
        elif range == self.Range.k4G:
            value = self.kFilterCtl_Range4G
            self.gsPerLSB = 0.002
        # 16G not supported; treat as 8G
        elif range == self.Range.k8G or range == self.Range.k16G:
            value = self.kFilterCtl_Range8G
            self.gsPerLSB = 0x004
        else:
            raise ValueError("Invalid range argument '%s'" % range)

        self.spi.write(
            [self.kRegWrite, self.kFilterCtlRegister, self.kFilterCtl_ODR_100Hz | value]
        )

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
        :returns: An object containing the acceleration measured on each axis in Gs.
        """
        if self.spi is None:
            return 0.0

        data = [self.kRegRead, self.kDataRegister + axis, 0, 0]
        data = self.spi.transaction(data)
        # Sensor is little endian... swap bytes
        rawAccel = (data[2] << 8) | data[1]
        return rawAccel * self.gsPerLSB

    def getAccelerations(self) -> Tuple[float, float, float]:
        """Get the acceleration of all axes in Gs.

        :returns: X,Y,Z tuple of acceleration measured on all axes in Gs.
        """
        if self.spi is None:
            return 0.0, 0.0, 0.0

        # Select the data address.
        data = [0] * 8
        data[0] = self.kRegRead
        data[1] = self.kDataRegister
        data = self.spi.transaction(data)

        # Sensor is little endian... swap bytes
        rawData = []
        for i in range(3):
            rawData.append((data[i * 2 + 2] << 8) | data[i * 2 + 1])

        return (
            rawData[0] * self.gsPerLSB,
            rawData[1] * self.gsPerLSB,
            rawData[2] * self.gsPerLSB,
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
