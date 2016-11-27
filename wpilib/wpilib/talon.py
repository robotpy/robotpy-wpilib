# validated: 2016-11-26 DS e44a6e227a89 athena/java/edu/wpi/first/wpilibj/Talon.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .pwmspeedcontroller import PWMSpeedController

__all__ = ["Talon"]

class Talon(PWMSpeedController):
    """
        Cross the Road Electronics (CTRE) Talon and Talon SR Speed Controller via PWM
    """

    def __init__(self, channel):
        """Constructor for a Talon (original or Talon SR)

        :param channel: The PWM channel that the Talon is attached to. 0-9 are on-board, 10-19 are on the MXP port
        :type  channel: int

        .. note ::

            The Talon uses the following bounds for PWM values. These values
            should work reasonably well for most controllers, but if users
            experience issues such as asymmetric behavior around the deadband
            or inability to saturate the controller in either direction,
            calibration is recommended.  The calibration procedure can be
            found in the Talon User Manual available from CTRE.

            - 2.037ms = full "forward"
            - 1.539ms = the "high end" of the deadband range
            - 1.513ms = center of the deadband range (off)
            - 1.487ms = the "low end" of the deadband range
            - 0.989ms = full "reverse"
        """
        super().__init__(channel)
        self.setBounds(2.037, 1.539, 1.513, 1.487, 0.989)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setSpeed(0.0)
        self.setZeroLatch()

        LiveWindow.addActuatorChannel("Talon", self.getChannel(), self)
        hal.report(hal.UsageReporting.kResourceType_Talon,
                   self.getChannel())
