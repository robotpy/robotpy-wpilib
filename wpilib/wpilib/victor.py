# validated: 2017-12-15 EN f9bece2ffbf7 edu/wpi/first/wpilibj/Victor.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .pwmspeedcontroller import PWMSpeedController

__all__ = ["Victor"]


class Victor(PWMSpeedController):
    """
        VEX Robotics Victor 888 Speed Controller via PWM
        
        The Vex Robotics Victor 884 Speed Controller can also be used with this
        class but may need to be calibrated per the Victor 884 user manual.
        
        .. note ::

            The Victor uses the following bounds for PWM values.  These
            values were determined empirically and optimized for the Victor
            888. These values should work reasonably well for Victor 884
            controllers also but if users experience issues such as
            asymmetric behaviour around the deadband or inability to saturate
            the controller in either direction, calibration is recommended.
            The calibration procedure can be found in the Victor 884 User
            Manual available from VEX Robotics:
            http://content.vexrobotics.com/docs/ifi-v884-users-manual-9-25-06.pdf
            
            - 2.027ms = full "forward"
            - 1.525ms = the "high end" of the deadband range
            - 1.507ms = center of the deadband range (off)
            - 1.49ms = the "low end" of the deadband range
            - 1.026ms = full "reverse"
        
        .. not_implemented: initVictor
    """

    def __init__(self, channel: int) -> None:
        """Constructor.

        :param channel: The PWM channel that the Victor is attached to. 0-9 are on-board, 10-19 are on the MXP port
        """
        super().__init__(channel)
        self.setBounds(2.027, 1.525, 1.507, 1.49, 1.026)
        self.setPeriodMultiplier(self.PeriodMultiplier.k2X)
        self.setSpeed(0)
        self.setZeroLatch()

        hal.report(hal.UsageReporting.kResourceType_Victor, self.getChannel())
        self.setName("Victor", self.getChannel())
