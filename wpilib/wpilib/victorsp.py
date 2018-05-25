# validated: 2017-12-15 EN f9bece2ffbf7 edu/wpi/first/wpilibj/VictorSP.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .pwmspeedcontroller import PWMSpeedController

__all__ = ["VictorSP"]


class VictorSP(PWMSpeedController):
    """
        VEX Robotics Victor SP Speed Controller via PWM
    """

    def __init__(self, channel: int) -> None:
        """Constructor.

        :param channel: The PWM channel that the VictorSP is attached to. 0-9 are on-board, 10-19 are on the MXP port.

        .. note ::

            The Talon uses the following bounds for PWM values. These values
            should work reasonably well for most controllers, but if users
            experience issues such as asymmetric behavior around the deadband
            or inability to saturate the controller in either direction,
            calibration is recommended.  The calibration procedure can be
            found in the VictorSP User Manual.

            - 2.004ms = full "forward"
            - 1.520ms = the "high end" of the deadband range
            - 1.500ms = center of the deadband range (off)
            - 1.480ms = the "low end" of the deadband range
            - 0.997ms = full "reverse"
        """
        super().__init__(channel)
        self.setBounds(2.004, 1.52, 1.50, 1.48, 0.997)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setSpeed(0)
        self.setZeroLatch()

        hal.report(hal.UsageReporting.kResourceType_VictorSP, self.getChannel())
        self.setName("VictorSP", self.getChannel())
