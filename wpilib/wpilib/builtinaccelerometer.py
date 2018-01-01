# validated: 2017-12-27 TW f9bece2ffbf7 edu/wpi/first/wpilibj/BuiltInAccelerometer.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in $(WIND_BASE)/WPILib.
#----------------------------------------------------------------------------

import hal

from .interfaces import Accelerometer
from .sensorbase import SensorBase

__all__ = ["BuiltInAccelerometer"]

class BuiltInAccelerometer(SensorBase):
    """Built-in accelerometer device

    This class allows access to the roboRIO's internal accelerometer.
    """

    Range = Accelerometer.Range

    def __init__(self, range=Accelerometer.Range.k8G):
        """Constructor.
        
        :param range: The range the accelerometer will measure.  Defaults to
            +/-8g if unspecified.
        :type  range: :class:`.Accelerometer.Range`
        """
        super().__init__()
        self.setRange(range)
        self.xEntry = None
        self.yEntry = None
        self.zEntry = None
        hal.report(hal.UsageReporting.kResourceType_Accelerometer, 0, 0,
                      "Built-in accelerometer")
        self.setName("BuiltInAccel", 0)

    def setRange(self, range):
        """Set the measuring range of the accelerometer.

        :param range: The maximum acceleration, positive or negative, that
                      the accelerometer will measure.
        :type  range: :class:`BuiltInAccelerometer.Range`
        """
        
        hal.setAccelerometerActive(False)

        if range == self.Range.k2G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_2G)
        elif range == self.Range.k4G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_4G)
        elif range == self.Range.k8G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_8G)
        elif range == self.Range.k16G:
            raise ValueError("16G range not supported (use k2G, k4G, or k8G)")
        else:
            raise ValueError("Invalid range argument '%s'" % range)

        hal.setAccelerometerActive(True)

    def getX(self):
        """
           :returns: The acceleration of the roboRIO along the X axis in
                     g-forces
           :rtype: float
        """
        return hal.getAccelerometerX()

    def getY(self):
        """
           :returns: The acceleration of the roboRIO along the Y axis in
                     g-forces
           :rtype: float
        """
        return hal.getAccelerometerY()

    def getZ(self):
        """
           :returns: The acceleration of the roboRIO along the Z axis in
                     g-forces
           :rtype: float
        """
        return hal.getAccelerometerZ()

    def initSendable(self, builder):
        builder.setSmartDashboardType("3AxisAccelerometer")
        builder.addDoubleProperty("X", self.getX, None)
        builder.addDoubleProperty("Y", self.getY, None)
        builder.addDoubleProperty("Z", self.getZ, None)
