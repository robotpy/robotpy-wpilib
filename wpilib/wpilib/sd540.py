# validated: 2015-12-23 DS fa903dd athena/java/edu/wpi/first/wpilibj/SD540.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .safepwm import SafePWM

__all__ = ["SD540"]

class SD540(SafePWM):
    """
        Mindsensors SD540 Speed Controller
           
        .. not_implemented: initSD540
    """

    def __init__(self, channel):
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
        self.setBounds(2.05, 1.55, 1.50, 1.44, .94)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setRaw(self.centerPwm)
        self.setZeroLatch()
        self.isInverted = False

        hal.HALReport(hal.HALUsageReporting.kResourceType_MindsensorsSD540,
                      self.getChannel())
        LiveWindow.addActuatorChannel("SD540", self.getChannel(), self)

    def free(self):
        LiveWindow.removeComponent(self)
        super().free()

    def set(self, speed, syncGroup=0):
        """Set the PWM value.

        The PWM value is set using a range of -1.0 to 1.0, appropriately
        scaling the value for the FPGA.

        :param speed: The speed to set.  Value should be between -1.0 and 1.0.
        :type  speed: float
        :param syncGroup: The update group to add this set() to, pending
            updateSyncGroup().  If 0, update immediately.
        """
        self.setSpeed(-speed if self.isInverted else speed)
        self.feed()
        
    def setInverted(self, isInverted):
        """
        Common interface for inverting the direction of a speed controller.

        :param isInverted: The state of inversion (True is inverted).
        """
        self.isInverted = isInverted

    def getInverted(self):
        """
        Common interface for inverting the direction of a speed controller.

        :returns: The state of inversion (True is inverted)
        """
        return self.isInverted

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
