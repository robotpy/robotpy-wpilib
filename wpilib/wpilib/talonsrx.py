#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .safepwm import SafePWM

__all__ = ["TalonSRX"]

class TalonSRX(SafePWM):
    """
        Cross the Road Electronics (CTRE) Talon SRX Speed Controller via PWM
        
        .. seealso:: See :class:`.CANTalon` for CAN control of Talon SRX.
        
        .. not_implemented: initTalonSRX
    """

    def __init__(self, channel):
        """Constructor for a TalonSRX connected via PWM.

        :param channel: The PWM channel that the TalonSRX is attached to. 0-9 are on-board, 10-19 are on the MXP port.
        :type  channel: int

        .. note ::

            The TalonSRX uses the following bounds for PWM values. These values
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
        self.setBounds(2.004, 1.52, 1.50, 1.48, .997)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setRaw(self.centerPwm)
        self.setZeroLatch()

        LiveWindow.addActuatorChannel("TalonSRX", self.getChannel(), self)
        hal.HALReport(hal.HALUsageReporting.kResourceType_TalonSRX,
                      self.getChannel())

    def set(self, speed, syncGroup=0):
        """Set the PWM value.

        The PWM value is set using a range of -1.0 to 1.0, appropriately
        scaling the value for the FPGA.

        :param speed: The speed to set.  Value should be between -1.0 and 1.0.
        :type  speed: float
        :param syncGroup: The update group to add this set() to, pending
            updateSyncGroup().  If 0, update immediately.
        """
        self.setSpeed(speed)
        self.feed()

    def get(self):
        """Get the recently set value of the PWM.

        :returns: The most recently set value for the PWM between -1.0 and 1.0.
        :rtype: float
        """
        return self.getSpeed()

    def pidWrite(self, output):
        """Write out the PID value as seen in the PIDOutput base object.

        :param output: Write out the PWM value as was found in the
            :class:`PIDController`.
        :type  output: float
        """
        self.set(output)
