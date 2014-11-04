#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in $(WIND_BASE)/WPILib.
#----------------------------------------------------------------------------

import hal

from .interfaces import Accelerometer
from .livewindowsendable import LiveWindowSendable

__all__ = ["BuiltInAccelerometer"]

class BuiltInAccelerometer(LiveWindowSendable):
    """Built-in accelerometer.

    This class allows access to the RoboRIO's internal accelerometer.
    """

    Range = Accelerometer.Range

    def __init__(self, range=Accelerometer.Range.k8G):
        """Constructor.
        :param range: The range the accelerometer will measure.  Defaults to
            +/-8g if unspecified.
        """
        self.setRange(range)
        hal.HALReport(hal.HALUsageReporting.kResourceType_Accelerometer, 0, 0,
                      "Built-in accelerometer")

    def setRange(self, range):
        hal.setAccelerometerActive(False)

        if range == self.Range.k2G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_2G)
        elif range == self.Range.k4G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_4G)
        elif range == self.Range.k8G:
            hal.setAccelerometerRange(hal.AccelerometerRange.kRange_8G)
        else:
            raise ValueError("16G range not supported (use k2G, k4G, or k8G)")

        hal.setAccelerometerActive(True)

    def getX(self):
        """:returns: The acceleration of the RoboRIO along the X axis in
            g-forces
        """
        return hal.getAccelerometerX()

    def getY(self):
        """:returns: The acceleration of the RoboRIO along the Y axis in
            g-forces
        """
        return hal.getAccelerometerY()

    def getZ(self):
        """:returns: The acceleration of the RoboRIO along the Z axis in
            g-forces
        """
        return hal.getAccelerometerZ()

    def getSmartDashboardType(self):
        return "Accelerometer"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("X", self.getX())
            table.putNumber("Y", self.getY())
            table.putNumber("Z", self.getZ())

    def startLiveWindowMode(self):
        pass

    def stopLiveWindowMode(self):
        pass
