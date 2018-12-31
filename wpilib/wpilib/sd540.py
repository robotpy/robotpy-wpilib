# validated: 2017-12-15 EN f9bece2ffbf7 edu/wpi/first/wpilibj/SD540.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .pwmspeedcontroller import PWMSpeedController

__all__ = ["SD540"]


class SD540(PWMSpeedController):
    """
        Mindsensors SD540 Speed Controller
           
        .. not_implemented: initSD540
    """

    def __init__(self, channel: int) -> None:
        """Constructor.

        :param channel: The PWM channel that the SD540 is attached to. 0-9 are on-board, 10-19 are on the MXP port
        
        .. note ::
        
           Note that the SD540 uses the following bounds for PWM values. These
           values should work reasonably well for most controllers, but if users
           experience issues such as asymmetric behavior around the deadband or
           inability to saturate the controller in either direction, calibration is
           recommended. The calibration procedure can be found in the SD540 User
           Manual available from Mindsensors.
           
           - 2.05ms = full "forward"
           - 1.55ms = the "high end" of the deadband range
           - 1.50ms = center of the deadband range (off)
           - 1.44ms = the "low end" of the deadband range
           - .94ms = full "reverse"
        
        """
        super().__init__(channel)
        self.setBounds(2.05, 1.55, 1.50, 1.44, 0.94)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setSpeed(0)
        self.setZeroLatch()

        hal.report(hal.UsageReporting.kResourceType_MindsensorsSD540, self.getChannel())
        self.setName("SD540", self.getChannel())
