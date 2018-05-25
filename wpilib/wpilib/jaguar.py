# validated: 2017-12-15 EN f9bece2ffbf7 edu/wpi/first/wpilibj/Jaguar.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .pwmspeedcontroller import PWMSpeedController

__all__ = ["Jaguar"]


class Jaguar(PWMSpeedController):
    """
        Texas Instruments / Vex Robotics Jaguar Speed Controller as a PWM device.
    """

    def __init__(self, channel: int) -> None:
        """Constructor.

        :param channel: The PWM channel that the Jaguar is attached to. 0-9 are on-board, 10-19 are on the MXP port
        """
        super().__init__(channel)
        # Input profile defined by Luminary Micro.
        #
        # Full reverse ranges from 0.671325ms to 0.6972211ms
        # Proportional reverse ranges from 0.6972211ms to 1.4482078ms
        # Neutral ranges from 1.4482078ms to 1.5517922ms
        # Proportional forward ranges from 1.5517922ms to 2.3027789ms
        # Full forward ranges from 2.3027789ms to 2.328675ms
        self.setBounds(2.31, 1.55, 1.507, 1.454, 0.697)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setSpeed(0)
        self.setZeroLatch()

        hal.report(hal.UsageReporting.kResourceType_Jaguar, self.getChannel())
        self.setName("Jaguar", self.getChannel())
