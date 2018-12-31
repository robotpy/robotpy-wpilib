# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/BuiltInAccelerometer.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2014-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in $(WIND_BASE)/WPILib.
# ----------------------------------------------------------------------------

import hal

from .interfaces import Accelerometer
from .sendablebuilder import SendableBuilder
from .sendablebase import SendableBase

__all__ = ["BuiltInAccelerometer"]


class BuiltInAccelerometer(SendableBase):
    """Built-in accelerometer device

    This class allows access to the roboRIO's internal accelerometer.
    """

    Range = Accelerometer.Range

    def __init__(self, range: Range = Accelerometer.Range.k8G) -> None:
        """Constructor.
        
        :param range: The range the accelerometer will measure.  Defaults to
            +/-8g if unspecified.
        """
        super().__init__()
        self.setRange(range)
        self.xEntry = None
        self.yEntry = None
        self.zEntry = None
        hal.report(
            hal.UsageReporting.kResourceType_Accelerometer,
            0,
            0,
            "Built-in accelerometer",
        )
        self.setName("BuiltInAccel", 0)

    def setRange(self, range: Range) -> None:
        """Set the measuring range of the accelerometer.

        :param range: The maximum acceleration, positive or negative, that
                      the accelerometer will measure.
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

    def getX(self) -> float:
        """
           :returns: The acceleration of the roboRIO along the X axis in
                     g-forces
        """
        return hal.getAccelerometerX()

    def getY(self) -> float:
        """
           :returns: The acceleration of the roboRIO along the Y axis in
                     g-forces
        """
        return hal.getAccelerometerY()

    def getZ(self) -> float:
        """
           :returns: The acceleration of the roboRIO along the Z axis in
                     g-forces
        """
        return hal.getAccelerometerZ()

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("3AxisAccelerometer")
        builder.addDoubleProperty("X", self.getX, None)
        builder.addDoubleProperty("Y", self.getY, None)
        builder.addDoubleProperty("Z", self.getZ, None)
