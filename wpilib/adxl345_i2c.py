#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .interfaces import Accelerometer
from .i2c import I2C
from .sensorbase import SensorBase

class ADXL345_I2C(SensorBase):
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

    class Axes:
        kX = 0x00
        kY = 0x02
        kZ = 0x04

    def __init__(self, port, range):
        """Constructor.

        :param port: The I2C bus port.
        :param range: The range (+ or -) that the accelerometer will measure.
        """
        self.i2c = I2C(port, self.kAddress)

        # Turn on the measurements
        self.i2c.write(self.kPowerCtlRegister, self.kPowerCtl_Measure)

        self.setRange(range)

        hal.HALReport(hal.HALUsageReporting.kResourceType_ADXL345,
                      hal.HALUsageReporting.kADXL345_I2C)

    # Accelerometer interface

    def setRange(self, range):
        """Set the measuring range of the accelerometer.

        :param range: The maximum acceleration, positive or negative, that
        the accelerometer will measure.
        """
        if range == self.k2G:
            value = 0
        elif range == self.k4G:
            value = 1
        elif range == self.k8G:
            value = 2
        elif range == self.k16G:
            value = 3
        else:
            value = 0

        # Specify the data format to read
        self.i2c.write(self.kDataFormatRegister, self.kDataFormat_FullRes | value)

    def getX(self):
        """Get the x axis acceleration

        :returns: The acceleration along the x axis in g-forces
        """
        return self.getAcceleration(self.Axes.kX)

    def getY(self):
        """Get the y axis acceleration

        :returns: The acceleration along the y axis in g-forces
        """
        return self.getAcceleration(self.Axes.kY)

    def getZ(self):
        """Get the z axis acceleration

        :returns: The acceleration along the z axis in g-forces
        """
        return self.getAcceleration(self.Axes.kZ)

    def getAcceleration(self, axis):
        """Get the acceleration of one axis in Gs.

        :param axis: The axis to read from.
        :returns: Acceleration of the ADXL345 in Gs.
        """
        data = self.i2c.read(self.kDataRegister + axis, 2)
        # Sensor is little endian... swap bytes
        rawAccel = (data[1] << 8) | data[0]
        return rawAccel * self.kGsPerLSB

    def getAccelerations(self):
        """Get the acceleration of all axes in Gs.

        :returns: X,Y,Z tuple of acceleration measured on all axes of the
            ADXL345 in Gs.
        """
        data = self.i2c.read(self.kDataRegister, 6)

        # Sensor is little endian... swap bytes
        rawData = []
        for i in range(3):
            rawData.append((data[i*2+1] << 8) | data[i*2])

        return (rawData[0] * self.kGsPerLSB,
                rawData[1] * self.kGsPerLSB,
                rawData[2] * self.kGsPerLSB)

    # TODO: Support LiveWindow
