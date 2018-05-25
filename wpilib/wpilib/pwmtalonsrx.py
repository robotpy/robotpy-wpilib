# validated: 2017-12-15 EN f9bece2ffbf7 edu/wpi/first/wpilibj/PWMTalonSRX.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .pwmspeedcontroller import PWMSpeedController

__all__ = ["PWMTalonSRX"]


class PWMTalonSRX(PWMSpeedController):
    """
    Cross the Road Electronics (CTRE) Talon SRX Speed Controller with PWM control.

    .. seealso:: See :class:`ctre.cantalon.CANTalon` for CAN control of Talon SRX.
    """

    def __init__(self, channel: int) -> None:
        """Constructor for a TalonSRX connected via PWM.

        :param channel: The PWM channel that the PWMTalonSRX is attached to. 0-9 are on-board, 10-19 are on the MXP port.

        .. note ::

            The PWMTalonSRX uses the following bounds for PWM values. These values
            should work reasonably well for most controllers, but if users
            experience issues such as asymmetric behavior around the deadband
            or inability to saturate the controller in either direction,
            calibration is recommended.  The calibration procedure can be
            found in the TalonSRX User Manual available from CTRE.

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

        hal.report(hal.UsageReporting.kResourceType_PWMTalonSRX, self.getChannel())
        self.setName("PWMTalonSRX", self.getChannel())
