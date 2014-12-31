#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .safepwm import SafePWM

__all__ = ["Victor"]

class Victor(SafePWM):
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
    
    def __init__(self, channel):
        """Constructor.

        :param channel: The PWM channel that the Victor is attached to. 0-9 are on-board, 10-19 are on the MXP port
        :type  channel: int
        """
        super().__init__(channel)
        self.setBounds(2.027, 1.525, 1.507, 1.49, 1.026)
        self.setPeriodMultiplier(self.PeriodMultiplier.k2X)
        self.setRaw(self.centerPwm)
        self.setZeroLatch()

        LiveWindow.addActuatorChannel("Victor", self.getChannel(), self)
        hal.HALReport(hal.HALUsageReporting.kResourceType_Victor,
                      self.getChannel())

    def set(self, speed, syncGroup=0):
        """Set the PWM value.

        The PWM value is set using a range of -1.0 to 1.0, appropriately
        scaling the value for the FPGA.

        :param speed: The speed to set.  Value should be between -1.0 and 1.0.
        :type  speed: float
        :param syncGroup: The update group to add this set to, pending
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
